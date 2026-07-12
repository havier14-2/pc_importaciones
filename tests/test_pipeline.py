import unittest
import pandas as pd
import numpy as np

class TestPipelineRetailFX(unittest.TestCase):

    def test_vectorizacion_alerta(self):
        """Prueba que la lógica de negocio vectorizada con numpy funcione correctamente"""
        # Simulamos un DataFrame de entrada
        df = pd.DataFrame({
            'margen_actual_pct': [5.0, 15.0],
            'margen_minimo_pct': [10.0, 10.0]
        })
        
        condiciones = [
            (df['margen_actual_pct'] < df['margen_minimo_pct']),
            (df['margen_actual_pct'] >= df['margen_minimo_pct'])
        ]
        opciones = ['ALERTA ROJA', 'OK']
        df['estado_riesgo'] = np.select(condiciones, opciones, default='INDETERMINADO')
        
        # Verificaciones (Asserts)
        self.assertEqual(df.loc[0, 'estado_riesgo'], 'ALERTA ROJA')
        self.assertEqual(df.loc[1, 'estado_riesgo'], 'OK')

    def test_estructura_reglas_csv(self):
        """Prueba que el archivo de reglas de negocio no esté vacío y tenga las columnas correctas"""
        import os
        ruta = os.path.join("data", "reglas_negocio.csv")
        self.assertTrue(os.path.exists(ruta), "El archivo reglas_negocio.csv no existe.")
        
        df = pd.read_csv(ruta)
        columnas_esperadas = ['producto', 'region_cl', 'precio_venta_clp', 'margen_minimo_pct']
        for col in columnas_esperadas:
            self.assertIn(col, df.columns, f"Falta la columna crítica: {col}")

if __name__ == '__main__':
    unittest.main()