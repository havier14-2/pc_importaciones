import pymysql
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Setup_Retail_FX")

def inicializar_mysql():
    try:
        conexion = pymysql.connect(host='localhost', user='root', password='')
        cursor = conexion.cursor()

        logger.info("Creando base de datos retail_fx_db...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS retail_fx_db;")
        cursor.execute("USE retail_fx_db;")

        # FUENTE 1: Sistema ERP (Inventario en Bodegas con costo en USD)
        cursor.execute("DROP TABLE IF EXISTS bodegas_tech;")
        cursor.execute('''
            CREATE TABLE bodegas_tech (
                id_producto VARCHAR(20),
                producto VARCHAR(100),
                stock_unidades INT,
                region_cl VARCHAR(50),
                costo_usd FLOAT
            )
        ''')

        # Insertamos el inventario. Ej: El MacBook cuesta 1500 USD de fábrica.
        datos_inventario = [
            ('SKU-MAC', 'MacBook Pro M3', 45, 'Metropolitana', 1500.0),
            ('SKU-IPH', 'iPhone 15 Pro', 120, 'Valparaíso', 999.0),
            ('SKU-MON', 'Monitor Dell 4K', 30, 'Metropolitana', 400.0),
            ('SKU-MAC', 'MacBook Pro M3', 15, 'Biobío', 1500.0)
        ]
        cursor.executemany('''
            INSERT INTO bodegas_tech (id_producto, producto, stock_unidades, region_cl, costo_usd)
            VALUES (%s, %s, %s, %s, %s)
        ''', datos_inventario)

        # DESTINO FINAL (LOAD): Data Warehouse exigido por la rúbrica
        cursor.execute("DROP TABLE IF EXISTS dw_riesgo_fx;")
        cursor.execute('''
            CREATE TABLE dw_riesgo_fx (
                fecha DATE,
                producto VARCHAR(100),
                region_cl VARCHAR(50),
                stock_unidades INT,
                costo_usd FLOAT,
                valor_dolar FLOAT,
                costo_total_clp FLOAT,
                precio_venta_clp FLOAT,
                margen_actual_pct FLOAT,
                estado_riesgo VARCHAR(50)
            )
        ''')

        conexion.commit()
        conexion.close()
        logger.info("¡Tablas MySQL creadas exitosamente para el Retail!")
        
    except Exception as e:
        logger.error(f"Error en MySQL: {e}")

if __name__ == "__main__":
    inicializar_mysql()