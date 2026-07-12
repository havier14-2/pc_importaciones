import os
import joblib
import logging
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Componentes de Scikit-learn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, accuracy_score, silhouette_score

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Modela_ML_FX")

def cargar_datos_dw():
    db_user = os.getenv("DB_USER", "root")
    db_pass = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "retail_fx_db")
    engine = create_engine(f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}')
    
    df = pd.read_sql("SELECT * FROM dw_riesgo_fx", engine)
    logger.info(f"Datos cargados desde el DW: {df.shape[0]} registros para entrenamiento.")
    return df

def entrenar_modelos():
    df = cargar_datos_dw()
    
    # ---------------------------------------------------------
    # PARTE 1: MODELO SUPERVISADO (Predicción de Alerta Roja)
    # ---------------------------------------------------------
    logger.info("Iniciando Fase 1: Aprendizaje Supervisado...")
    
    # Definir Características (X) y Objetivo (y)
    X = df[['producto', 'region_cl', 'stock_unidades', 'costo_usd', 'valor_dolar']]
    # Convertimos a binario: 1 si es ALERTA ROJA, 0 si está OK
    y = np.where(df['estado_riesgo'].str.contains('ALERTA ROJA'), 1, 0)
    
    # Separación de datos (Train / Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Pipeline de Preprocesamiento
    cat_cols = ['producto', 'region_cl']
    num_cols = ['stock_unidades', 'costo_usd', 'valor_dolar']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
        ]
    )
    
    # Definición de Algoritmos candidatos para comparación (Exigencia IEE 2.1.1)
    pipe_rf = Pipeline([('preproc', preprocessor), ('clf', RandomForestClassifier(random_state=42))])
    pipe_lr = Pipeline([('preproc', preprocessor), ('clf', LogisticRegression(random_state=42))])
    
    # Ajuste de Hiperparámetros (Tuning con GridSearchCV) para Random Forest
    param_grid_rf = {
        'clf__n_estimators': [50, 100],
        'clf__max_depth': [None, 5, 10],
        'clf__min_samples_split': [2, 5]
    }
    
    logger.info("Ejecutando Tuning de Hiperparámetros mediante GridSearchCV...")
    grid_search = GridSearchCV(pipe_rf, param_grid_rf, cv=3, scoring='f1', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    best_model_rf = grid_search.best_estimator_
    
    # Evaluar Regresión Logística para comparar
    pipe_lr.fit(X_train, y_train)
    
    # Métricas de Evaluación (Exigencia IEP 2.2.2)
    preds_rf = best_model_rf.predict(X_test)
    preds_lr = pipe_lr.predict(X_test)
    
    logger.info("=== COMPARATIVA DE MODELOS SUPERVISADOS ===")
    logger.info(f"Random Forest (Optimizado) - Accuracy: {accuracy_score(y_test, preds_rf):.4f}")
    logger.info(f"Regresión Logística - Accuracy: {accuracy_score(y_test, preds_lr):.4f}")
    
    print("\nReporte de Clasificación (Random Forest Seleccionado):")
    print(classification_report(y_test, preds_rf, target_names=['OK (Sano)', 'ALERTA ROJA']))
    
    # Guardar modelo supervisado ganador
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model_rf, "models/rf_predictor_riesgo.pkl")
    logger.info("Modelo supervisado exportado exitosamente a 'models/rf_predictor_riesgo.pkl'")
    
    # ---------------------------------------------------------
    # PARTE 2: MODELO NO SUPERVISADO (Clustering K-Means)
    # ---------------------------------------------------------
    logger.info("Iniciando Fase 2: Aprendizaje No Supervisado...")
    
    # Agruparemos basándonos en variables financieras continuas
    X_unsupervised = df[['valor_dolar', 'margen_actual_pct', 'costo_total_clp']]
    
    # Pipeline para K-Means
    pipe_cluster = Pipeline([
        ('scaler', StandardScaler()),
        ('kmeans', KMeans(n_clusters=3, random_state=42, n_init=10))
    ])
    
    df['cluster_riesgo'] = pipe_cluster.fit_predict(X_unsupervised)
    
    # Métrica de Cohesión (Silhouette Score) para evaluar el agrupamiento
    sil_sc = silhouette_score(StandardScaler().fit_transform(X_unsupervised), df['cluster_riesgo'])
    logger.info(f"K-Means finalizado con 3 clusters. Coeficiente de Silhouette: {sil_sc:.4f}")
    
    # Guardar modelo de clustering
    joblib.dump(pipe_cluster, "models/kmeans_cluster_riesgo.pkl")
    logger.info("Modelo no supervisado exportado exitosamente a 'models/kmeans_cluster_riesgo.pkl'")
    
    # Mostrar un resumen analítico de los clusters para la defensa de negocio
    print("\nPerfilamiento de Clusters de Riesgo Cambiario:")
    resumen = df.groupby('cluster_riesgo')[['valor_dolar', 'margen_actual_pct', 'costo_total_clp']].mean()
    print(resumen)

if __name__ == "__main__":
    entrenar_modelos()