import os
import requests
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar configuración de entorno
load_dotenv()

# Conexión al Data Warehouse para cargar el histórico
db_user = os.getenv("DB_USER", "root")
db_pass = os.getenv("DB_PASSWORD", "")
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "retail_fx_db")
engine = create_engine(f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}')

# Inicializar aplicación Dash con estilos limpios
app = Dash(__name__)
app.title = "Retail Tech FX - Panel de Control Financiero"

# Diseño de la Interfaz del Dashboard (Layout)
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f4f6f9'}, children=[
    
    # Encabezado Corporativo
    html.Div(style={'backgroundColor': '#1e3a8a', 'color': 'white', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px'}, children=[
        html.H1("Retail Tech FX: Sistema Analítico y Preventivo de Riesgo Cambiario", style={'margin': '0', 'fontSize': '26px'}),
        html.P("Monitoreo de Márgenes Comerciales frente a fluctuaciones de la divisa USD/CLP (EFT)", style={'margin': '5px 0 0 0', 'opacity': '0.9'})
    ]),
    
    # Fila de Filtros y Control Histórico
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            html.H3("Filtro de Producto Histórico", style={'marginTop': '0', 'color': '#333'}),
            dcc.Dropdown(
                id='selector-producto',
                options=[{'label': 'Todos los Productos', 'value': 'ALL'}] + 
                        [{'label': p, 'value': p} for p in ['MacBook Pro M3', 'iPhone 15 Pro', 'Monitor Dell 4K']],
                value='ALL',
                clearable=False
            )
        ]),
        
        # Módulo del Simulador de Negocio con Inteligencia Artificial (Llama a la API)
        html.Div(style={'flex': '2', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'borderLeft': '5px solid #10b981'}, children=[
            html.H3("🔮 Simulador de Riesgo Cambiario en Tiempo Real (Inferencia via API REST)", style={'marginTop': '0', 'color': '#065f46'}),
            html.Div(style={'display': 'flex', 'gap': '15px', 'flexWrap': 'wrap'}, children=[
                html.Div([
                    html.Label("Producto a Evaluar:"),
                    dcc.Dropdown(id='sim-producto', options=[{'label': p, 'value': p} for p in ['MacBook Pro M3', 'iPhone 15 Pro', 'Monitor Dell 4K']], value='MacBook Pro M3', clearable=False, style={'width': '180px'})
                ]),
                html.Div([
                    html.Label("Región Bodega:"),
                    dcc.Dropdown(id='sim-region', options=[{'label': r, 'value': r} for r in ['Metropolitana', 'Valparaíso', 'Biobío']], value='Metropolitana', clearable=False, style={'width': '180px'})
                ]),
                html.Div([
                    html.Label("Dólar Proyectado ($):"),
                    dcc.Slider(id='sim-dolar', min=800, max=1100, step=10, value=960, marks={i: f"${i}" for i in range(800, 1101, 100)})
                ]),
            ]),
            html.Div(id='resultado-simulacion-api', style={'marginTop': '15px', 'padding': '10px', 'borderRadius': '6px', 'fontWeight': 'bold'})
        ])
    ]),
    
    # Fila de Gráficos Analíticos
    html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            html.H4("Evolución Temporal de Márgenes y Cotización del Dólar", style={'marginTop': '0'}),
            dcc.Graph(id='grafico-tendencia')
        ]),
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            html.H4("Distribución de Alertas en el Tiempo", style={'marginTop': '0'}),
            dcc.Graph(id='grafico-alertas')
        ])
    ])
])

# ---------------------------------------------------------
# CALLBACK 1: Actualizar Gráficos Históricos desde el Data Warehouse
# ---------------------------------------------------------
@app.callback(
    [Output('grafico-tendencia', 'figure'),
     Output('grafico-alertas', 'figure')],
    [Input('selector-producto', 'value')]
)
def actualizar_graficos_historicos(producto_seleccionado):
    # Leer datos frescos del DW MySQL
    df = pd.read_sql("SELECT * FROM dw_riesgo_fx", engine)
    
    if producto_seleccionado != 'ALL':
        df = df[df['producto'] == producto_seleccionado]
    
    # Gráfico 1: Tendencia Temporal del Margen
    fig_tendencia = px.line(
        df, x='fecha', y='margen_actual_pct', color='producto',
        title="Fluctuación del Margen Porcentual Real por Fecha",
        labels={'margen_actual_pct': 'Margen Real (%)', 'fecha': 'Fecha de Cotización'},
        template='plotly_white'
    )
    fig_tendencia.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Pérdida Económica")
    
    # Gráfico 2: Alertas de Margen Sanos vs Alertas Rojas
    fig_alertas = px.histogram(
        df, x='producto', color='estado_riesgo', barmode='group',
        title="Conteo Histórico de Alertas de Margen",
        color_discrete_map={'OK (Margen Sano)': '#10b981', 'ALERTA ROJA (Pérdida/Bajo Margen)': '#ef4444'},
        template='plotly_white'
    )
    
    return fig_tendencia, fig_alertas

# ---------------------------------------------------------
# CALLBACK 2: Integración en Tiempo Real con la API REST (Inferencia de ML)
# ---------------------------------------------------------
@app.callback(
    Output('resultado-simulacion-api', 'children'),
    Output('resultado-simulacion-api', 'style'),
    [Input('sim-producto', 'value'),
     Input('sim-region', 'value'),
     Input('sim-dolar', 'value')]
)
def consultar_api_predictiva(producto, region, valor_dolar):
    # Datos por defecto operacionales simulados para enviar a la API
    stock_falso = 45 if "MacBook" in producto else (120 if "iPhone" in producto else 30)
    costo_falso = 1500.0 if "MacBook" in producto else (999.0 if "iPhone" in producto else 400.0)
    
    payload = {
        "producto": producto,
        "region_cl": region,
        "stock_unidades": stock_falso,
        "costo_usd": costo_falso,
        "valor_dolar": float(valor_dolar)
    }
    
    try:
        # Petición HTTP POST dirigida a la API REST de FastAPI (Puerto 8000)
        url_api = "http://127.0.0.1:8000/predict/risk"
        respuesta = requests.post(url_api, json=payload, timeout=3)
        
        if respuesta.status_code == 200:
            datos_api = respuesta.json()
            alerta_activa = datos_api["alerta_roja_proyectada"]
            probabilidad = datos_api["probabilidad_riesgo_pct"]
            mensaje = datos_api["mensaje_negocio"]
            
            # Estilos dinámicos según el dictamen del modelo de ML
            if alerta_activa:
                color_fondo = '#fee2e2'
                color_texto = '#991b1b'
                borde = '1px solid #f87171'
                texto_salida = f"❌ {mensaje} (Probabilidad de Alerta: {probabilidad}%)"
            else:
                color_fondo = '#d1fae5'
                color_texto = '#065f46'
                borde = '1px solid #34d399'
                texto_salida = f"✅ {mensaje} (Probabilidad de Alerta: {probabilidad}%)"
                
            estilo = {'backgroundColor': color_fondo, 'color': color_texto, 'border': borde, 'padding': '12px', 'borderRadius': '6px'}
            return texto_salida, estilo
        else:
            return "⚠️ API REST disponible pero retornó un error de procesamiento.", {'color': '#d97706'}
            
    except requests.exceptions.ConnectionError:
        return "🔌 Error de Conexión: La API REST (FastAPI) en el puerto 8000 está apagada. Enciéndela para activar la predicción de Machine Learning.", {'color': '#ef4444', 'backgroundColor': '#fef2f2', 'padding': '10px', 'borderRadius': '6px'}

if __name__ == "__main__":
    app.run(debug=True, port=8050)