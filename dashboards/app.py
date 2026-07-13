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

# Diseño de la Interfaz del Dashboard (Layout Mejorado y Espaciado)
app.layout = html.Div(style={'fontFamily': 'Segoe UI, Arial, sans-serif', 'padding': '25px', 'backgroundColor': '#f8fafc', 'minHeight': '100vh'}, children=[
    
    # Encabezado Corporativo Moderno
    html.Div(style={'backgroundColor': '#1e3a8a', 'color': 'white', 'padding': '25px', 'borderRadius': '12px', 'marginBottom': '25px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}, children=[
        html.H1("Retail Tech FX: Panel de Riesgo Cambiario", style={'margin': '0', 'fontSize': '28px', 'fontWeight': '600'}),
        html.P("Monitoreo de Costos de Internación frente a fluctuaciones de la divisa USD/CLP (EFT)", style={'margin': '8px 0 0 0', 'opacity': '0.85', 'fontSize': '15px'})
    ]),
    
    # Contenedor Superior: Filtro Histórico (Izquierda) y Simulador IA (Derecha)
    html.Div(style={'display': 'flex', 'gap': '25px', 'marginBottom': '25px', 'flexWrap': 'wrap'}, children=[
        
        # Panel Filtro Histórico
        html.Div(style={'flex': '1', 'minWidth': '300px', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)', 'borderTop': '4px solid #1e3a8a'}, children=[
            html.H3("🔍 Filtro de Histórico", style={'marginTop': '0', 'color': '#1e293b', 'fontSize': '18px', 'marginBottom': '15px'}),
            html.Label("Seleccionar Producto:", style={'fontWeight': '500', 'color': '#64748b', 'marginBottom': '8px', 'display': 'block'}),
            dcc.Dropdown(
                id='selector-producto',
                options=[{'label': 'Todos los Productos', 'value': 'ALL'}],
                value='ALL',
                clearable=False
            )
        ]),
        
        # Módulo del Simulador de Negocio con IA (Diseño Vertical Ampliado para evitar solapamiento)
        html.Div(style={'flex': '2', 'minWidth': '500px', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)', 'borderLeft': '5px solid #10b981'}, children=[
            html.H3("🔮 Simulador de Costos en Tiempo Real (Inferencia ML)", style={'marginTop': '0', 'color': '#065f46', 'fontSize': '18px', 'marginBottom': '20px'}),
            
            # Inputs bien distribuidos de forma vertical/bloque
            html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
                html.Div([
                    html.Label("Producto a Evaluar en Escenario Cambiario:", style={'fontWeight': '600', 'color': '#334155', 'display': 'block', 'marginBottom': '8px'}),
                    dcc.Dropdown(id='sim-producto', options=[], value='', clearable=False, style={'width': '100%'})
                ]),
                html.Div([
                    html.Label("Definir Valor del Dólar Proyectado ($ CLP):", style={'fontWeight': '600', 'color': '#334155', 'display': 'block', 'marginBottom': '15px'}),
                    html.Div(style={'padding': '0 15px'}, children=[
                        dcc.Slider(
                            id='sim-dolar', 
                            min=800, 
                            max=1100, 
                            step=10, 
                            value=950, 
                            marks={i: {'label': f"${i}", 'style': {'color': '#475569', 'fontSize': '12px'}} for i in range(800, 1101, 50)}
                        )
                    ])
                ]),
            ]),
            
            # Caja de Respuesta de la Inferencia
            html.Div(id='resultado-simulacion-api', style={'marginTop': '25px', 'transition': 'all 0.3s ease'})
        ])
    ]),
    
    # Fila Inferior: Gráficos Analíticos de Pantalla Completa
    html.Div(style={'display': 'flex', 'gap': '25px', 'flexWrap': 'wrap'}, children=[
        html.Div(style={'flex': '1', 'minWidth': '450px', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}, children=[
            dcc.Graph(id='grafico-tendencia')
        ]),
        html.Div(style={'flex': '1', 'minWidth': '450px', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}, children=[
            dcc.Graph(id='grafico-alertas')
        ])
    ])
])

# ---------------------------------------------------------
# CALLBACK 1: Carga Dinámica de Opciones y Gráficos Históricos Legibles
# ---------------------------------------------------------
@app.callback(
    [Output('selector-producto', 'options'),
     Output('sim-producto', 'options'),
     Output('sim-producto', 'value'),
     Output('grafico-tendencia', 'figure'),
     Output('grafico-alertas', 'figure')],
    [Input('selector-producto', 'value')],
    [State('sim-producto', 'value')]
)
def actualizar_panel_y_opciones(producto_seleccionado, producto_sim_actual):
    df = pd.read_sql("SELECT * FROM dw_riesgo_fx", engine)
    
    if df.empty:
        fig_vacia = px.line(title="Sin datos disponibles en dw_riesgo_fx")
        return [{'label': 'Todos', 'value': 'ALL'}], [], '', fig_vacia, fig_vacia

    # Asegurar que la fecha sea un formato de tiempo correcto para Plotly
    df['fecha'] = pd.to_datetime(df['fecha'])

    productos_unicos = sorted(df['producto'].unique())
    opciones_dropdown = [{'label': 'Todos los Productos', 'value': 'ALL'}] + [{'label': p, 'value': p} for p in productos_unicos]
    opciones_simulador = [{'label': p, 'value': p} for p in productos_unicos]
    
    val_sim_defecto = producto_sim_actual if producto_sim_actual in productos_unicos else productos_unicos[0]

    if producto_seleccionado == 'ALL':
        # ESTRATEGIA DE CLARIDAD: Si son todos los productos, agrupamos por mes y mostramos el promedio ponderado
        df_resumido = df.groupby([df['fecha'].dt.to_period('M'), 'producto'])['costo_internacion_clp'].mean().reset_index()
        df_resumido['fecha'] = df_resumido['fecha'].dt.to_timestamp()
        
        fig_tendencia = px.scatter(
            df_resumido, x='fecha', y='costo_internacion_clp', color='producto',
            title="Costo de Internación Promedio Mensual por Producto (Vista Global)",
            labels={'costo_internacion_clp': 'Costo Promedio ($ CLP)', 'fecha': 'Mes de Operación'},
            template='plotly_white'
        )
        fig_tendencia.update_traces(marker=dict(size=10, opacity=0.7))
    else:
        # Si selecciona uno solo, mostramos su línea temporal exacta paso a paso
        df_filtrado = df[df['producto'] == producto_seleccionado].sort_values('fecha')
        fig_tendencia = px.line(
            df_filtrado, x='fecha', y='costo_internacion_clp',
            title=f"Línea de Tiempo Analítica: {producto_seleccionado}",
            labels={'costo_internacion_clp': 'Costo Internación ($ CLP)', 'fecha': 'Fecha de Importación'},
            template='plotly_white',
            line_shape='spline'
        )
        fig_tendencia.update_traces(line_color='#1e3a8a', line_width=2.5)
    
    # Agregar el techo presupuestario común de forma clara
    fig_tendencia.add_hline(y=800000, line_dash="dash", line_color="#ef4444", annotation_text="Techo Presupuestario ($800K CLP)", annotation_position="top left")
    fig_tendencia.update_layout(margin={'t': 50, 'b': 40, 'l': 50, 'r': 40}, hovermode="x unified")
    
    # Gráfico 2: Frecuencia de Alertas
    df_alertas = df if producto_seleccionado == 'ALL' else df[df['producto'] == producto_seleccionado]
    fig_alertas = px.histogram(
        df_alertas, x='producto', color='estado_riesgo', barmode='group',
        title="Clasificación Agrupada de Operaciones por Umbral de Alerta",
        labels={'producto': 'Producto Analizado', 'count': 'N° de Transacciones'},
        color_discrete_map={'OPERACIÓN OPTIMIZADA': '#10b981', 'ALERTA ROJA (Sobrecosto Predictivo)': '#ef4444'},
        template='plotly_white'
    )
    fig_alertas.update_layout(margin={'t': 50, 'b': 40, 'l': 40, 'r': 40}, xaxis_tickangle=-30)
    
    return opciones_dropdown, opciones_simulador, val_sim_defecto, fig_tendencia, fig_alertas

# ---------------------------------------------------------
# CALLBACK 2: Integración en Tiempo Real con FastAPI (Modelo de Regresión)
# ---------------------------------------------------------
@app.callback(
    [Output('resultado-simulacion-api', 'children'),
     Output('resultado-simulacion-api', 'style')],
    [Input('sim-producto', 'value'),
     Input('sim-dolar', 'value')]
)
def consultar_api_predictiva(producto, valor_dolar):
    if not producto:
        return "Seleccione un producto válido para comenzar la simulación cambiaria.", {
            'color': '#475569', 'backgroundColor': '#f1f5f9', 'padding': '12px', 'borderRadius': '8px', 'border': '1px solid #cbd5e1'
        }

    # FIX CRÍTICO: Envío de parámetros como tupla válida (producto,) para evitar el error de SQLAlchemy/Pandas
    query = "SELECT categoria, cantidad_unidades, precio_fob_usd, arancel_aduanero_pct FROM dw_riesgo_fx WHERE producto = %s LIMIT 1"
    df_base = pd.read_sql(query, engine, params=(producto,))
    
    if df_base.empty:
        categoria, cantidad, precio, arancel = "General", 1, 100.0, 6.0
    else:
        categoria = df_base.iloc[0]['categoria']
        cantidad = int(df_base.iloc[0]['cantidad_unidades'])
        precio = float(df_base.iloc[0]['precio_fob_usd'])
        arancel = float(df_base.iloc[0]['arancel_aduanero_pct'])

    payload = {
        "producto": producto,
        "categoria": categoria,
        "cantidad_unidades": cantidad,
        "precio_fob_usd": precio,
        "valor_dolar": float(valor_dolar),
        "arancel_aduanero_pct": arancel
    }
    
    try:
        url_api = "http://127.0.0.1:8000/predict/risk"
        respuesta = requests.post(url_api, json=payload, timeout=3)
        
        if respuesta.status_code == 200:
            datos_api = respuesta.json()
            sobrecosto_activo = datos_api["alerta_sobrecosto"]
            mensaje = datos_api["mensaje_negocio"]
            
            if sobrecosto_activo:
                color_fondo, color_texto, borde, icono = '#fef2f2', '#991b1b', '1px solid #f87171', "❌ "
            else:
                color_fondo, color_texto, borde, icono = '#ecfdf5', '#065f46', '1px solid #34d399', "✅ "
                
            estilo = {
                'backgroundColor': color_fondo, 'color': color_texto, 'border': borde, 
                'padding': '15px', 'borderRadius': '8px', 'whiteSpace': 'pre-line', 'fontWeight': '600', 'fontSize': '14px'
            }
            return f"{icono}{mensaje}", estilo
        else:
            return "⚠️ La API falló al procesar los datos de regresión del modelo.", {
                'color': '#b45309', 'backgroundColor': '#fffbeb', 'padding': '12px', 'borderRadius': '8px', 'border': '1px solid #fcd34d'
            }
            
    except requests.exceptions.ConnectionError:
        return "🔌 Servicio de Inferencia Inactivo: FastAPI (Puerto 8000) no responde. Enciende tu backend de ML para activar predicciones en vivo.", {
            'color': '#b91c1c', 'backgroundColor': '#fef2f2', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #fca5a5', 'fontWeight': '600'
        }

if __name__ == "__main__":
    app.run(debug=True, port=8050)