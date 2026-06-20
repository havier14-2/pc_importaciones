import os
import requests
import logging
import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("ETL_Motor_FX")

def ejecutar_pipeline():
    logger.info("1. EXTRACT: Iniciando extracción de las 3 fuentes...")

    # --- FUENTE 1: API REST (Mindicador - Dólar) ---
    resp = requests.get("https://mindicador.cl/api/dolar", timeout=10)
    df_api = pd.DataFrame(resp.json()['serie'])
    df_api['fecha'] = pd.to_datetime(df_api['fecha']).dt.date
    df_api = df_api.rename(columns={'valor': 'valor_dolar'})
    logger.info(f"Extraídos {len(df_api)} días de cotización del dólar.")

    # --- FUENTE 2: MySQL (Inventario ERP) ---
    engine = create_engine('mysql+pymysql://root:@localhost/retail_fx_db')
    df_mysql = pd.read_sql("SELECT * FROM bodegas_tech", engine)
    logger.info("Extraído el inventario actual de MySQL.")

    # --- FUENTE 3: CSV (Reglas de Negocio / Márgenes) ---
    ruta_csv = os.path.join("data", "reglas_negocio.csv")
    df_csv = pd.read_csv(ruta_csv)
    logger.info("Extraídas reglas de negocio del CSV.")

    # ---------------------------------------------------------
    # 2. TRANSFORM: El Cruce Maestro
    # ---------------------------------------------------------
    logger.info("2. TRANSFORM: Cruzando datos y calculando riesgo cambiario...")
    
    # Unimos Inventario con Reglas (Llave: producto y region_cl)
    df_inventario = pd.merge(df_mysql, df_csv, on=['producto', 'region_cl'], how='inner')

    # Hacemos un "Cross Join" para evaluar el inventario contra CADA DÍA del dólar
    df_master = df_inventario.merge(df_api, how='cross')

    # Cálculos Financieros
    # ¿Cuánto nos cuesta el producto en pesos chilenos según el dólar de ESE día?
    df_master['costo_total_clp'] = df_master['costo_usd'] * df_master['valor_dolar']
    
    # ¿Cuál es nuestro porcentaje de ganancia real? ((Venta - Costo) / Venta) * 100
    df_master['margen_actual_pct'] = ((df_master['precio_venta_clp'] - df_master['costo_total_clp']) / df_master['precio_venta_clp']) * 100

    # REGLA DE NEGOCIO: Si el margen real cae por debajo del mínimo tolerado, disparamos la alerta
    df_master['estado_riesgo'] = df_master.apply(
        lambda row: 'ALERTA ROJA (Pérdida/Bajo Margen)' if row['margen_actual_pct'] < row['margen_minimo_pct'] else 'OK (Margen Sano)', 
        axis=1
    )

    # Ordenamos y limpiamos las columnas para el Data Warehouse
    df_final = df_master[[
        'fecha', 'producto', 'region_cl', 'stock_unidades', 'costo_usd', 
        'valor_dolar', 'costo_total_clp', 'precio_venta_clp', 'margen_actual_pct', 'estado_riesgo'
    ]].sort_values(by=['fecha', 'producto'], ascending=[True, True])

    # ---------------------------------------------------------
    # 3. LOAD: Cargar a MySQL
    # ---------------------------------------------------------
    logger.info("3. LOAD: Guardando tabla analítica en MySQL...")
    df_final.to_sql('dw_riesgo_fx', engine, if_exists='replace', index=False)
    
    logger.info("¡Pipeline ETL completado con éxito! Listo para el Dashboard.")
    print(df_final.head(10).to_string(index=False))

if __name__ == "__main__":
    ejecutar_pipeline()