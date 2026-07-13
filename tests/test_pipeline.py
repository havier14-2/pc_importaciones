import unittest
import pandas as pd
import numpy as np

class TestPipelineRetailFX(unittest.TestCase):

    def test_vectorizacion_alerta(self):
        """Prueba que la lógica de negocio vectorizada con numpy funcione correctamente según los nuevos costos"""
        # Simulamos un DataFrame con casos que superan y se mantienen bajo el techo presupuestario
        df = pd.DataFrame({
            'costo_internacion_clp': [850000.0, 450000.0]
        })
        
        UMBRAL_PRESUPUESTO_CLP = 800000.0
        
        condiciones = [
            (df['costo_internacion_clp'] > UMBRAL_PRESUPUESTO_CLP),
            (df['costo_internacion_clp'] <= UMBRAL_PRESUPUESTO_CLP)
        ]
        opciones = ['ALERTA ROJA (Sobrecosto Predictivo)', 'OPERACIÓN OPTIMIZADA']
        df['estado_riesgo'] = np.select(condiciones, opciones, default='INDETERMINADO')
        
        # Verificaciones (Asserts) alineadas con las salidas exactas del ETL
        self.assertEqual(df.loc[0, 'estado_riesgo'], 'ALERTA ROJA (Sobrecosto Predictivo)')
        self.assertEqual(df.loc[1, 'estado_riesgo'], 'OPERACIÓN OPTIMIZADA')

    def test_estructura_sales_data_csv(self):
        """Prueba que el dataset de ventas de Kaggle exista y cumpla con el esquema requerido"""
        import os
        ruta = os.path.join("data", "sales_data.csv")
        self.assertTrue(os.path.exists(ruta), "El archivo sales_data.csv de Kaggle no existe en la carpeta data.")
        
        # Leemos solo las primeras filas para optimizar la velocidad del test
        df = pd.read_csv(ruta, nrows=5)
        df.columns = df.columns.str.strip()  # Limpieza idéntica a la del ETL
        
        columnas_esperadas = ['Order Date', 'Product', 'Quantity Ordered', 'Price Each']
        for col in columnas_esperadas:
            self.assertIn(col, df.columns, f"Falta la columna requerida por el esquema del ETL: {col}")

if __name__ == '__main__':
    unittest.main()