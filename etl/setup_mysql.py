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

        # FUENTE 3: Base de Datos Relacional (Reglas de Negocio / Impuestos en Chile)
        logger.info("Creando tabla producto_importacion...")
        cursor.execute("DROP TABLE IF EXISTS producto_importacion;")
        cursor.execute('''
            CREATE TABLE producto_importacion (
                product VARCHAR(255) PRIMARY KEY,
                categoria VARCHAR(100),
                arancel_aduanero_pct FLOAT,
                costo_logistico_usd FLOAT
            )
        ''')

        # Insertamos las reglas de negocio para los productos reales del CSV de Kaggle
        datos_reglas = [
            ('Macbook Pro Laptop', 'Computación', 6.00, 45.00),
            ('iPhone', 'Telefonía', 6.00, 15.00),
            ('Google Phone', 'Telefonía', 6.00, 15.00),
            ('AA Batteries (4-pack)', 'Accesorios', 0.00, 2.00),
            ('AAA Batteries (4-pack)', 'Accesorios', 0.00, 2.00),
            ('USB-C Charging Cable', 'Accesorios', 6.00, 3.00),
            ('Lightning Charging Cable', 'Accesorios', 6.00, 3.00),
            ('Bose SoundSport Headphones', 'Audio', 6.00, 8.00),
            ('Apple Airpods Headphones', 'Audio', 6.00, 8.00),
            ('Wired Headphones', 'Audio', 6.00, 4.00),
            ('27in FHD Monitor', 'Monitores', 6.00, 25.00),
            ('27in 4K Gaming Monitor', 'Monitores', 6.00, 30.00),
            ('34in Ultrawide Monitor', 'Monitores', 6.00, 35.00),
            ('Flatscreen TV', 'Entretenimiento', 6.00, 40.00),
            ('20in Monitor', 'Monitores', 6.00, 20.00),
            ('Vareebadd Phone', 'Telefonía', 6.00, 15.00),
            ('LG Washing Machine', 'Línea Blanca', 6.00, 80.00),
            ('LG Dryer', 'Línea Blanca', 6.00, 80.00),
            ('ThinkPad Laptop', 'Computación', 6.00, 40.00)
        ]
        
        cursor.executemany('''
            INSERT INTO producto_importacion (product, categoria, arancel_aduanero_pct, costo_logistico_usd)
            VALUES (%s, %s, %s, %s)
        ''', datos_reglas)

        # DESTINO FINAL (LOAD): Data Warehouse exigido por la rúbrica
        logger.info("Creando tabla del Data Warehouse (dw_riesgo_fx)...")
        cursor.execute("DROP TABLE IF EXISTS dw_riesgo_fx;")
        cursor.execute('''
            CREATE TABLE dw_riesgo_fx (
                fecha DATE,
                producto VARCHAR(100),
                categoria VARCHAR(100),
                cantidad_unidades INT,
                precio_fob_usd FLOAT,
                valor_dolar FLOAT,
                costo_total_fob_usd FLOAT,
                arancel_aplicado_pct FLOAT,
                costo_internacion_clp FLOAT
            )
        ''')

        conexion.commit()
        conexion.close()
        logger.info("¡Estructura e integraciones listas en MySQL!")
        
    except Exception as e:
        logger.error(f"Error en MySQL: {e}")

if __name__ == "__main__":
    inicializar_mysql()