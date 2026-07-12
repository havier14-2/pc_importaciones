import os
import joblib
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("API_Riesgo_FX")

app = FastAPI(
    title="Retail Tech FX - API de Monitoreo Preventivo",
    description="API Corporativa para predecir el riesgo de margen por fluctuaciones del dólar (USD/CLP).",
    version="1.0.0"
)

# --- CARGA DEL MODELO ENTRENADO ---
RUTA_MODELO = os.path.join("models", "rf_predictor_riesgo.pkl")

if os.path.exists(RUTA_MODELO):
    try:
        modelo = joblib.load(RUTA_MODELO)
        logger.info("Modelo supervisado de Machine Learning cargado con éxito en la API.")
    except Exception as e:
        logger.error(f"Error al deserializar el modelo .pkl: {e}")
        modelo = None
else:
    logger.error(f"No se encontró el archivo del modelo en {RUTA_MODELO}. Asegúrate de ejecutar 'models/train.py' primero.")
    modelo = None

# --- MODELOS DE VALIDACIÓN DE ENTRADA Y SALIDA (Pydantic) ---
class DatosSolicitudRiesgo(BaseModel):
    producto: str = Field(..., example="MacBook Pro M3", description="Nombre exacto del producto tecnológico")
    region_cl: str = Field(..., example="Metropolitana", description="Región de Chile donde se ubica la bodega")
    stock_unidades: int = Field(..., gt=0, example=45, description="Cantidad actual en inventario físico")
    costo_usd: float = Field(..., gt=0.0, example=1500.0, description="Costo unitario de importación de fábrica en USD")
    valor_dolar: float = Field(..., gt=0.0, example=955.5, description="Cotización proyectada del Dólar Observado (USD/CLP)")

class RespuestaPrediccionRiesgo(BaseModel):
    producto: str
    region_cl: str
    alerta_roja_proyectada: bool
    probabilidad_riesgo_pct: float
    mensaje_negocio: str

# --- ENDPOINTS ---

@app.get("/", tags=["General"])
def estado_api():
    """
    Endpoint base para comprobar la salud del servicio (Health Check).
    """
    return {
        "estado": "Operativa", 
        "modelo_cargado": modelo is not None,
        "contexto": "EFT - Programación para la Ciencia de Datos"
    }

@app.post("/predict/risk", response_model=RespuestaPrediccionRiesgo, tags=["Machine Learning"])
def predecir_riesgo_cambiario(datos: DatosSolicitudRiesgo):
    """
    Endpoint principal: Recibe variables operacionales y del tipo de cambio, 
    y evalúa preventivamente si el producto sufrirá una destrucción de margen (Alerta Roja).
    """
    if modelo is None:
        raise HTTPException(
            status_code=503, 
            detail="El servicio de Machine Learning no está disponible (modelo .pkl ausente)."
        )
    
    try:
        # 1. Estructurar la entrada en el DataFrame exacto que espera el Pipeline del modelo
        import pandas as pd
        df_input = pd.DataFrame([{
            'producto': datos.producto,
            'region_cl': datos.region_cl,
            'stock_unidades': datos.stock_unidades,
            'costo_usd': datos.costo_usd,
            'valor_dolar': datos.valor_dolar
        }])
        
        # 2. Ejecutar la inferencia del modelo
        prediccion = modelo.predict(df_input)[0]  # Retorna 0 o 1
        probabilidades = modelo.predict_proba(df_input)[0]  # Retorna [prob_0, prob_1]
        
        prob_alerta_roja = probabilidades[1] * 100
        alerta_activa = bool(prediccion == 1)
        
        # 3. Construir mensaje corporativo enfocado en impacto de negocio
        if alerta_activa:
            mensaje = f"CRÍTICO: El tipo de cambio a ${datos.valor_dolar} destruye el margen mínimo tolerado para {datos.producto} en la región {datos.region_cl}."
        else:
            mensaje = f"ESTABLE: El producto mantiene un margen comercial saludable bajo esta cotización cambiaria."
            
        return RespuestaPrediccionRiesgo(
            producto=datos.producto,
            region_cl=datos.region_cl,
            alerta_roja_proyectada=alerta_activa,
            probabilidad_riesgo_pct=round(prob_alerta_roja, 2),
            mensaje_negocio=mensaje
        )
        
    except Exception as e:
        logger.error(f"Error interno durante la inferencia: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al procesar la predicción: {str(e)}")