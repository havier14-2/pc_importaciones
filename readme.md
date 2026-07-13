# 💻 Retail Tech FX: Pipeline ETL & Monitoreo de Riesgo Cambiario

Este proyecto es una solución corporativa de Inteligencia de Negocios (BI) diseñada para una cadena de Retail Tecnológico. El sistema automatiza la extracción de datos de inventario, cruza los costos de importación con la cotización diaria en tiempo real del Dólar Observado (USD/CLP) y genera alertas visuales inmediatas cuando las fluctuaciones de la divisa destruyen los márgenes de ganancia mínimos permitidos.

## 🏗️ Arquitectura de Datos (3 Fuentes Heterogéneas)

El motor ETL integra tres tipos de orígenes de datos completamente distintos para poblar un Data Warehouse analítico en MySQL:

1. **API REST (Dinámica y Externa):** Conexión directa a https://mindicador.cl/ para extraer la serie de tiempo real con el valor diario del Dólar Observado en Chile.  
2. **Base de Datos Relacional (Origen ERP Interno):** Tabla en MySQL (`bodegas_tech`) que almacena el stock físico actual y el costo original de importación de fábrica en dólares (USD).  
3. **Archivo Plano (CSV - Reglas de Negocio):** Archivo estático `reglas_negocio.csv` que define el precio de venta final en pesos chilenos (CLP) y el umbral de margen de ganancia mínimo que la empresa tolera por sucursal.

---

## 🚀 Instalación y Requisitos Iniciales

### 1. Requisitos del Sistema

- **Python 3.9 o superior** instalado en el sistema.  
- **XAMPP** con el módulo de MySQL encendido (ejecutándose en el puerto estándar `3306`).

### 2. Preparación del Entorno

Antes de iniciar, abre la terminal en la raíz del proyecto e instala las librerías necesarias con el siguiente comando:

```bash
pip install pandas requests sqlalchemy pymysql dash plotly
```

---

## 🛠️ Guía de Ejecución y Configuración en Windows

Para simplificar el despliegue inicial, el proyecto cuenta con un entorno preparado para ejecutarse de forma centralizada. Sigue este orden estricto para inicializar y desplegar el sistema en cualquier máquina.

### Paso 1: Inicialización Única con Jupyter Notebook

La forma más rápida de inicializar el entorno por primera vez sin usar comandos manuales es a través del archivo interactivo de presentación.

1. Abre tu editor de código (por ejemplo, VS Code) y carga el archivo `note_etl.ipynb`.  
2. Asegúrate de tener XAMPP y MySQL activos.  
3. Ejecuta la **Fase 0** (las primeras celdas del Notebook). Esto ejecutará automáticamente los scripts en segundo plano para:
   - Crear la base de datos `retail_fx_db` en tu MySQL local.
   - Poblar las tablas origen con los datos de inventario en USD.
   - Invocar el pipeline ETL por primera vez para descargar la serie histórica del dólar y rellenar el Data Warehouse.

### Paso 2: Desplegar la Interfaz Visual (Dashboard)

Una vez inicializados los datos a través del Notebook, el sistema está listo para la visualización.

Ejecuta en terminal:

```bash
python app.py
```

Luego abre el navegador e ingresa a:

```text
http://127.0.0.1:8050/
```

---

## ⚙️ Configuración de la Automatización Diaria en Windows

Para cumplir con el requisito de funcionamiento autónomo sin intervención humana, el proyecto delega la actualización de datos a un script por lotes de Windows (`.bat`) conectado al sistema operativo.

### ¿Cómo funciona el archivo `.bat`?

El archivo `automatizacion.bat`, ubicado en la raíz del proyecto, es completamente portátil. Utiliza la variable del sistema `%~dp0`, lo que significa que detecta dinámicamente la carpeta en la que se encuentra guardado.

No requiere configurar rutas manuales fijas en el código; al ejecutarse (ya sea mediante doble clic o por el sistema operativo), resolverá automáticamente los directorios, invocará Python y actualizará MySQL de forma silenciosa.

### Programación Automática del Sistema (Paso a Paso en Windows)

Para ejecutar el pipeline automáticamente todas las mañanas:

1. Presiona **Inicio** → busca **Programador de tareas (Task Scheduler)** → abre la aplicación.  
2. Haz clic en **Crear tarea básica...**  
3. Asigna un nombre (ejemplo: `ETL_Actualizacion_Retail_FX`).  
4. Selecciona **Diariamente** como desencadenador.  
5. Configura una hora recomendada (ejemplo: **06:00 AM**).  
6. Selecciona **Iniciar un programa**.  
7. En **Programa o script**, selecciona el archivo `automatizacion.bat`.  
8. En **Iniciar en (opcional)**, pega la ruta de la carpeta raíz del proyecto.  
9. Finaliza el asistente.

Desde ese momento, Windows ejecutará automáticamente el script según el horario definido, manteniendo actualizado el Data Warehouse y permitiendo que el Dashboard en Dash refleje alertas críticas de riesgo cambiario en tiempo real.


### EJECUTAR PROYECTO

1. Abrir xampp y activar MySQL en el puerto 3306
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `.\lanzar_proyecto.ps1`
