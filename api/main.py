import os
import joblib
import logging
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("API_Riesgo_FX")

app = FastAPI(
    title="Retail Tech FX - API de Monitoreo Preventivo",
    description="API Corporativa para predecir costos de internación y alertas de sobrecosto por volatilidad cambiaria.",
    version="2.0.0"
)

# --- CARGA DEL MODELO REFACTORIZADO (REGRESIÓN) ---
RUTA_MODELO = os.path.join("models", "rf_predictor_riesgo.pkl")

if os.path.exists(RUTA_MODELO):
    try:
        modelo = joblib.load(RUTA_MODELO)
        logger.info("Modelo predictivo de Regresión (Random Forest) cargado con éxito en la API.")
    except Exception as e:
        logger.error(f"Error al deserializar el modelo .pkl: {e}")
        modelo = None
else:
    logger.error(f"No se encontró el archivo del modelo en {RUTA_MODELO}. Ejecuta 'models/train.py' primero.")
    modelo = None

# --- MODELOS DE VALIDACIÓN DE ENTRADA Y SALIDA (Pydantic) ---
class DatosSolicitudRiesgo(BaseModel):
    producto: str = Field(..., example="Wired Headphones", description="Nombre exacto del producto según dataset")
    categoria: str = Field(..., example="Electronics", description="Categoría asignada en base de datos")
    cantidad_unidades: int = Field(..., gt=0, example=5, description="Cantidad solicitada en la orden de compra")
    precio_fob_usd: float = Field(..., gt=0.0, example=11.99, description="Precio unitario cobrado por el proveedor en EE.UU.")
    valor_dolar: float = Field(..., gt=0.0, example=945.8, description="Cotización del dólar observada o proyectada (API)")
    arancel_aduanero_pct: float = Field(6.0, ge=0.0, example=6.0, description="Porcentaje de arancel aduanero chileno")

class RespuestaPrediccionRiesgo(BaseModel):
    producto: str
    costo_internacion_estimado_clp: float
    alerta_sobrecosto: bool
    mensaje_negocio: str

# --- ENDPOINTS ---

@app.get("/", tags=["General"])
def estado_api():
    """
    Endpoint de contingencia y chequeo de salud del servicio (Health Check).
    """
    return {
        "estado": "Operativa", 
        "modelo_regresor_cargado": modelo is not None,
        "contexto": "EFT - Programación para la Ciencia de Datos"
    }

@app.post("/predict/risk", response_model=RespuestaPrediccionRiesgo, tags=["Machine Learning"])
def predecir_riesgo_cambiario(datos: DatosSolicitudRiesgo):
    """
    Endpoint Principal: Recibe las condiciones de la orden de compra y el valor del dólar,
    utiliza la Inteligencia Artificial para estimar el costo de internación final en CLP
    y evalúa dinámicamente si rompe los techos presupuestarios corporativos.
    """
    if modelo is None:
        raise HTTPException(
            status_code=503, 
            detail="El servicio analítico no está disponible (modelo .pkl ausente o corrupto)."
        )
    
    try:
        # 1. Mapear la entrada pydantic exactamente a las columnas que espera el pipeline del train.py
        df_input = pd.DataFrame([{
            'producto': datos.producto,
            'categoria': datos.categoria,
            'cantidad_unidades': datos.cantidad_unidades,
            'precio_fob_usd': datos.precio_fob_usd,
            'valor_dolar': datos.valor_dolar,
            'arancel_aduanero_pct': datos.arancel_aduanero_pct
        }])
        
        # 2. Inferencia: Predecir el valor continuo en CLP (Regresión)
        costo_predicho_clp = float(modelo.predict(df_input)[0])
        
        # 3. Lógica de negocio para Alerta Automatizada (Umbral financiero simulado: $800.000 CLP)
        UMBRAL_MAXIMO_PERMITIDO = 800000.0
        alerta_activa = costo_predicho_clp > UMBRAL_MAXIMO_PERMITIDO
        
        if alerta_activa:
            mensaje = (f"CRÍTICO: El costo de internación proyectado de ${costo_predicho_clp:,.0f} CLP "
                       f"excede el presupuesto máximo configurado de ${UMBRAL_MAXIMO_PERMITIDO:,.0f} CLP "
                       f"debido a la presión cambiaria de ${datos.valor_dolar} CLP/USD.")
        else:
            mensaje = (f"OPERACIÓN OPTIMIZADA: El costo proyectado es de ${costo_predicho_clp:,.0f} CLP. "
                       f"Se mantiene bajo los parámetros de tolerancia financiera de la empresa.")
            
        return RespuestaPrediccionRiesgo(
            producto=datos.producto,
            costo_internacion_estimado_clp=round(costo_predicho_clp, 2),
            alerta_sobrecosto=alerta_activa,
            mensaje_negocio=mensaje
        )
        
    except Exception as e:
        logger.error(f"Error interno durante el procesamiento de la inferencia: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el motor predictivo: {str(e)}")