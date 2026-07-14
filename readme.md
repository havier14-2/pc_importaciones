# 💻 Retail Tech FX
## Plataforma Inteligente de Monitoreo de Riesgo Cambiario para Importaciones Tecnológicas

Retail Tech FX es una plataforma de Inteligencia de Negocios y Machine Learning desarrollada para apoyar la toma de decisiones en empresas importadoras de hardware tecnológico.

La solución automatiza la obtención de información desde múltiples fuentes, procesa los datos mediante un pipeline ETL, entrena un modelo predictivo basado en Machine Learning y expone sus funcionalidades a través de una arquitectura de microservicios utilizando FastAPI, Dash y Docker.

---

# 🚀 Características

- Extracción automática de datos desde múltiples fuentes.
- Pipeline ETL completamente automatizado.
- Limpieza y transformación eficiente mediante Pandas y NumPy.
- Predicción del costo de importación utilizando Random Forest Regressor.
- Segmentación exploratoria mediante K-Means.
- API REST desarrollada con FastAPI.
- Dashboard interactivo desarrollado con Dash y Plotly.
- Despliegue mediante Docker Compose.
- Automatización mediante scripts Batch y PowerShell.
- Tolerancia a fallos frente a indisponibilidad de servicios externos.

---

# 🏗️ Arquitectura del Sistema

```
                  Mindicador.cl API
                         │
                         │
        CSV ─────────► ETL Python ◄──────── MySQL
                         │
                         ▼
                 Dataset Procesado
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
Random Forest Regressor              K-Means
        │                                 │
        └──────────────┬──────────────────┘
                       ▼
                   FastAPI
                       │
                       ▼
                Dashboard Dash
                       │
                       ▼
                    Usuario
```

---

# 📁 Estructura del Proyecto

```
RetailTechFX/
│
├── api/                    # API REST FastAPI
├── dashboard/              # Dashboard Dash
├── data/
│   ├── raw/
│   └── processed/
├── etl/
│   ├── setup_mysql.py
│   └── etl_riesgo_fx.py
├── models/
│   ├── train.py
│   └── modelo_random_forest.pkl
├── tests/
├── docker-compose.yml
├── requirements.txt
├── automatizacion.bat
├── lanzar_proyecto.ps1
└── README.md
```

---

# ⚙️ Requisitos

Antes de ejecutar el proyecto asegúrate de tener instalado:

- Python 3.9 o superior
- MySQL (XAMPP o MySQL Server)
- Docker Desktop
- Git (opcional)

Verifica además que:

- MySQL esté ejecutándose en el puerto **3306**
- Docker Desktop esté iniciado

---

# 📦 Instalación

Clona el repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd RetailTechFX
```

Instala las dependencias:

```bash
py -m pip install -r requirements.txt
```

---

# 🗄️ Inicializar la Base de Datos

Inicia MySQL desde XAMPP (o tu servidor MySQL).

Luego ejecuta:

```bash
py etl/setup_mysql.py
```

Este script creará automáticamente:

- Base de datos `retail_fx_db`
- Tablas necesarias
- Datos iniciales

---

# 🔄 Ejecutar el Pipeline ETL

Una vez creada la base de datos, ejecuta:

```bash
py etl/etl_riesgo_fx.py
```

El pipeline realiza automáticamente:

- Extracción de datos CSV
- Lectura desde MySQL
- Consumo de la API Mindicador.cl
- Limpieza de datos
- Transformación
- Ingeniería de características
- Consolidación del dataset

Si la API gubernamental no responde, el sistema utiliza un valor de contingencia para evitar que el proceso falle.

---

# 🤖 Entrenar el Modelo de Machine Learning

Ejecuta:

```bash
py models/train.py
```

Este proceso:

- Entrena el modelo Random Forest Regressor.
- Evalúa su desempeño.
- Guarda automáticamente el modelo entrenado (.pkl).

Salida esperada:

```
Modelo entrenado correctamente.
Archivo modelo_random_forest.pkl generado.
```

---

# 🚀 Ejecutar Localmente

## Iniciar la API

```bash
uvicorn api.main:app --reload
```

Disponible en:

```
http://localhost:8000
```

Documentación Swagger:

```
http://localhost:8000/docs
```

---

## Iniciar el Dashboard

En otra terminal:

```bash
py dashboard/app.py
```

Disponible en:

```
http://localhost:8050
```

---

# 🐳 Despliegue con Docker

Con Docker Desktop abierto, ejecutar:

```bash
docker compose up --build
```

Esto levantará automáticamente:

| Servicio | Puerto |
|----------|---------|
| FastAPI | 8000 |
| Dashboard | 8050 |

Accesos:

Dashboard

```
http://localhost:8050
```

Swagger

```
http://localhost:8000/docs
```

Para detener los servicios:

```bash
docker compose down
```

---

# ⚙️ Automatización

El proyecto incorpora dos métodos de automatización.

## Batch

```bash
automatizacion.bat
```

Ejecuta automáticamente:

- Pruebas unitarias
- Pipeline ETL
- Entrenamiento del modelo

---

## PowerShell

```powershell
.\lanzar_proyecto.ps1
```

Este script:

- Inicializa la base de datos
- Ejecuta el ETL
- Entrena el modelo
- Levanta la API
- Inicia el Dashboard

---

# 📊 Tecnologías Utilizadas

- Python
- Pandas
- NumPy
- Scikit-Learn
- FastAPI
- Dash
- Plotly
- MySQL
- Docker
- Docker Compose
- Git

---

# 🧪 Pruebas

Para ejecutar las pruebas unitarias:

```bash
python -m unittest discover tests
```

---

# 🧰 Troubleshooting

## Error

```
ConnectionRefusedError
```

### Causa

MySQL no está iniciado.

### Solución

Abrir XAMPP e iniciar el servicio MySQL.

---

## Error

```
Unknown database 'retail_fx_db'
```

### Causa

La base de datos aún no existe.

### Solución

Ejecutar:

```bash
py etl/setup_mysql.py
```

---

## Error

```
ReadTimeout
```

### Explicación

La API de Mindicador.cl no respondió dentro del tiempo esperado.

No requiere intervención.

El sistema utilizará automáticamente un valor de contingencia para continuar el procesamiento.

---

## Error

```
Servicio de Inferencia Inactivo
```

### Causa

El Dashboard no logra comunicarse con la API.

### Solución

- Si trabajas con Docker, verifica que el Dashboard apunte al servicio `api_ml`.
- Si trabajas localmente, asegúrate de que FastAPI esté ejecutándose antes de abrir el Dashboard.

---

# 📈 Resultado Esperado

Al finalizar correctamente la ejecución:

- Base de datos creada.
- Dataset consolidado.
- Modelo entrenado.
- API REST disponible.
- Dashboard operativo.
- Predicciones listas para ser consultadas desde la interfaz web.

---

# 👥 Autores

**Carolina Aguirre**

**Javier Albornoz**

Ingeniería en Informática — Duoc UC

Proyecto desarrollado para la asignatura de Programación para Ciencia de Datos.