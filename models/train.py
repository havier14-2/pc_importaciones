import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Librerías de Machine Learning
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
import joblib

# Cargar variables de entorno
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Train_IA_Retail_FX")

def entrenar_modelo_predictivo():
    logger.info("Iniciando fase de Machine Learning...")

    # 1. Conexión al Data Warehouse (MySQL)
    db_user = os.getenv("DB_USER", "root")
    db_pass = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "retail_fx_db")
    url_conexion = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
    engine = create_engine(url_conexion)

    # Extraer los datos unificados por el ETL
    logger.info("Extrayendo datos consolidados desde dw_riesgo_fx...")
    df = pd.read_sql("SELECT * FROM dw_riesgo_fx", engine)

    if df.empty:
        raise ValueError("El Data Warehouse está vacío. Ejecuta el script ETL primero.")

    # 2. Preparación de Features (X) y Variable Objetivo (y)
    # Excluimos variables que contengan directamente el cálculo del destino o fechas
    X = df[['producto', 'categoria', 'cantidad_unidades', 'precio_fob_usd', 'valor_dolar', 'arancel_aduanero_pct']]
    y = df['costo_internacion_clp']

    # División del dataset (Train/Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)    

    # 3. Pipeline de Preprocesamiento Estructurado (OneHotEncoding para categóricas)
    columnas_categoricas = ['producto', 'categoria']
    columnas_numericas = ['cantidad_unidades', 'precio_fob_usd', 'valor_dolar', 'arancel_aduanero_pct']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), columnas_categoricas)
        ],
        remainder='passthrough'
    )

    # Pipeline del Modelo: Preprocesamiento + Regresor
    modelo_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(random_state=42))
    ])

    # 4. Optimización de Hiperparámetros (GridSearchCV)
    logger.info("Optimizando hiperparámetros con GridSearchCV...")
    param_grid = {
        'regressor__n_estimators': [50, 100],
        'regressor__max_depth': [None, 10]
    }
    
    grid_search = GridSearchCV(modelo_pipeline, param_grid, cv=3, scoring='r2', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    mejor_modelo = grid_search.best_estimator_
    logger.info(f"Mejores parámetros encontrados: {grid_search.best_params_}")

    # 5. Evaluación del Modelo de Regresión
    y_pred = mejor_modelo.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"Métricas del Modelo -> RMSE: {rmse:.2f} CLP | R² Score: {r2*100:.2f}%")

    # 6. Serialización y Persistencia (Guardar el .pkl)
    os.makedirs("models", exist_ok=True)
    ruta_guardado = os.path.join("models", "rf_predictor_riesgo.pkl")
    joblib.dump(mejor_modelo, ruta_guardado)
    logger.info(f"¡Modelo guardado exitosamente en {ruta_guardado}!")

    # ---------------------------------------------------------
    # 7. GENERACIÓN DE GRÁFICOS CIENTÍFICOS (Requisito de Rúbrica)
    # ---------------------------------------------------------
    os.makedirs("static", exist_ok=True)
    sns.set_theme(style="whitegrid")

    # Gráfico 1: Importancia de Variables (Supervisado)
    logger.info("Generando gráfico de Importancia de Variables...")
    importancias = grid_search.best_estimator_._final_estimator.feature_importances_
    # Extraer nombres de las columnas transformadas por el OneHotEncoder
    nombres_cat = grid_search.best_estimator_.named_steps['preprocessor'].transformers_[0][1].get_feature_names_out(columnas_categoricas)
    todos_los_features = list(nombres_cat) + columnas_numericas
    
    # Tomamos el top 6 de variables que más pesan
    df_imp = pd.DataFrame({'Feature': todos_los_features, 'Importancia': importancias}).sort_values(by='Importancia', ascending=False).head(6)
    
    plt.figure(figsize=(10, 5))
    sns.barplot(x='Importancia', y='Feature', data=df_imp, palette='viridis')
    plt.title('Top 6 Factores Clave en la Variación de Costos de Internación (CLP)')
    plt.tight_layout()
    plt.savefig('static/feature_importance.png')
    plt.close()

    # Gráfico 2: K-Means Clustering (No Supervisado)
    logger.info("Generando gráfico No Supervisado (K-Means Clustering)...")
    # Agrupamos las transacciones para visualizar sensibilidad frente al dólar
    X_clustering = df[['valor_dolar', 'costo_internacion_clp']].dropna()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster_riesgo'] = kmeans.fit_predict(X_clustering)
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x='valor_dolar', y='costo_internacion_clp', 
        hue='cluster_riesgo', palette='Set2', data=df, alpha=0.7
    )
    plt.title('Segmentación No Superficial de Embarques por Nivel de Riesgo Cambiario')
    plt.xlabel('Valor del Dólar Observado (API)')
    plt.ylabel('Costo Proyectado Internación (CLP)')
    plt.legend(title='Clusters de Riesgo')
    plt.tight_layout()
    plt.savefig('static/clusters_sensibilidad.png')
    plt.close()
    
    logger.info("¡Gráficos guardados con éxito en la carpeta static/!")

if __name__ == "__main__":
    entrenar_modelo_predictivo()