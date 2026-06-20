import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine

# 1. CONEXIÓN A LA BASE DE DATOS MySQL
engine = create_engine('mysql+pymysql://root:@localhost/retail_fx_db')

def obtener_datos():
    df = pd.read_sql("SELECT * FROM dw_riesgo_fx", engine)
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

app = dash.Dash(__name__)
app.title = "Retail FX: Control de Márgenes"

df_inicial = obtener_datos()
regiones_disponibles = sorted(df_inicial['region_cl'].unique().tolist())

# 2. DISEÑO DE LA INTERFAZ
app.layout = html.Div([
    html.H1("💻 Retail Tech FX: Monitoreo de Riesgo Cambiario (USD/CLP)", 
            style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif', 'color': '#2c3e50', 'padding': '20px'}),

    # Filtro Dinámico por REGIÓN
    html.Div([
        html.Label("Seleccione Sucursal / Región:", style={'fontWeight': 'bold', 'fontFamily': 'Arial'}),
        dcc.Dropdown(
            id='filtro-region',
            options=[{'label': r, 'value': r} for r in regiones_disponibles],
            value=regiones_disponibles[0] if regiones_disponibles else None,
            clearable=False,
            style={'width': '50%', 'marginTop': '10px'}
        )
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'border': '1px solid #dee2e6', 'borderRadius': '5px', 'margin': '0 40px 20px 40px'}),

    # Tarjetas KPI
    html.Div(id='tarjetas-kpi', style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '0 40px 20px 40px', 'fontFamily': 'Arial'}),

    # Gráficos
    html.Div([
        html.Div([dcc.Graph(id='grafico-dolar')], style={'width': '49%', 'display': 'inline-block', 'border': '1px solid #dee2e6', 'borderRadius': '5px'}),
        html.Div([dcc.Graph(id='grafico-barras-margen')], style={'width': '49%', 'display': 'inline-block', 'float': 'right', 'border': '1px solid #dee2e6', 'borderRadius': '5px'})
    ], style={'margin': '0 40px'})
])

# 3. LÓGICA DEL MOTOR DASH (Callbacks)
@app.callback(
    [Output('tarjetas-kpi', 'children'),
     Output('grafico-dolar', 'figure'),
     Output('grafico-barras-margen', 'figure')],
    [Input('filtro-region', 'value')]
)
def actualizar_dashboard(region_seleccionada):
    df = obtener_datos()
    df_filtrado = df[df['region_cl'] == region_seleccionada].copy()

    if df_filtrado.empty:
        return html.Div("Sin datos."), go.Figure(), go.Figure()

    # --- DATOS DEL ÚLTIMO DÍA ---
    fecha_mas_reciente = df_filtrado['fecha'].max()
    df_hoy = df_filtrado[df_filtrado['fecha'] == fecha_mas_reciente]
    
    valor_dolar_hoy = df_hoy['valor_dolar'].iloc[0]
    
    productos_en_riesgo = df_hoy[df_hoy['estado_riesgo'].str.contains('ALERTA ROJA')]
    cantidad_riesgo = len(productos_en_riesgo)

    if cantidad_riesgo > 0:
        texto_alerta = f"{cantidad_riesgo} PRODUCTO(S) EN RIESGO"
        color_alerta = "#e74c3c"
    else:
        texto_alerta = "MÁRGENES SANOS: SIN ALERTAS"
        color_alerta = "#27ae60"

    estilo_kpi = {'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '5px', 'width': '48%', 'textAlign': 'center', 'border': '1px solid #e0e0e0', 'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'}

    tarjetas = [
        html.Div([
            html.H4("Cotización Dólar Observado (Último Cierre)", style={'color': '#7f8c8d'}),
            html.H2(f"${valor_dolar_hoy:,.1f} CLP", style={'color': '#2980b9', 'fontSize': '32px'})
        ], style=estilo_kpi),
        
        html.Div([
            html.H4("Estado Actual de la Sucursal", style={'color': '#7f8c8d'}),
            html.H2(texto_alerta, style={'color': color_alerta, 'fontSize': '28px', 'fontWeight': 'bold'})
        ], style={**estilo_kpi, 'borderBottom': f'6px solid {color_alerta}'})
    ]

    # --- GRÁFICO 1: EVOLUCIÓN DEL DÓLAR ---
    df_dolar = df_filtrado.drop_duplicates(subset=['fecha']).sort_values('fecha')
    fig_dolar = px.area(df_dolar, x='fecha', y='valor_dolar',
                         title="Contexto Macroeconómico: Evolución del Dólar",
                         labels={'fecha': 'Fecha', 'valor_dolar': 'Valor USD ($)'})
    fig_dolar.update_traces(line_color='#2980b9', fillcolor='rgba(41, 128, 185, 0.2)')
    fig_dolar.update_layout(plot_bgcolor='white', yaxis_tickformat="$,.0f", xaxis=dict(showgrid=False))

    # --- GRÁFICO 2: BARRAS DE ALERTA ---
    # Usamos color='estado_riesgo' para agrupar por alerta de forma nativa e indestructible
    fig_barras = px.bar(df_filtrado.sort_values('fecha'), x='fecha', y='margen_actual_pct', 
                        color='estado_riesgo', barmode='group',
                        hover_data=['producto'], # Te mostrará el nombre del producto si pones el mouse encima
                        color_discrete_map={'ALERTA ROJA (Pérdida/Bajo Margen)': '#e74c3c', 'OK (Margen Sano)': '#27ae60'},
                        title="Evolución del Margen de Ganancia (%) por Producto",
                        labels={'fecha': 'Fecha', 'margen_actual_pct': 'Margen Real (%)', 'estado_riesgo': 'Estado de Riesgo'})
    
    fig_barras.update_layout(plot_bgcolor='white', showlegend=True, yaxis_ticksuffix="%")
    # Movemos la leyenda arriba para que no estorbe
    fig_barras.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    return tarjetas, fig_dolar, fig_barras

if __name__ == '__main__':
    app.run(debug=True)