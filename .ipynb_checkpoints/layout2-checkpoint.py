from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Cargar datasets
df_combinado = pd.read_csv("data/predicted_with_anomalies_and_future.csv", parse_dates=["Fecha"])
df_errores = pd.read_csv("data/Errores.csv")
df_resultados = pd.read_csv("data/Resultados_Modelos.csv")

# Variables disponibles
variables = ["Presion", "Temperatura", "Volumen"]
clientes = df_combinado["Client_ID"].unique()

# Definir tooltips para las métricas
tooltips = {
"rmse-metrica": "RMSE y MAE: indican el nivel de error del modelo LSTM al predecir las variables clave. Cuanto más bajos estos valores, más precisa es la predicción del consumo esperado.",
"mae-metrica": "RMSE y MAE: indican el nivel de error del modelo LSTM al predecir las variables clave. Cuanto más bajos estos valores, más precisa es la predicción del consumo esperado.",
"anomalias-filtro": "Anomalías Filtro: Son los puntos identificados como anómalos por Isolation Forest pero dentro del periodo visible filtrado. Esto permite un enfoque contextual en la revisión.",
"anomalias-historicas": "Anomalías Históricas: Representan el total de puntos detectados como anómalos por Isolation Forest en todo el histórico analizado para este cliente.",
"coincidencias": "Coincidencias: Corresponden a los casos donde ambos modelos (Isolation Forest y LSTM) detectaron comportamientos anómalos en al menos una de las tres variables. Isolation Forest identifica puntos que se salen del comportamiento normal del cliente. LSTM predice el consumo esperado de presión, temperatura y volumen. Si el valor real se desvía mucho (según umbrales técnicos), lo marca como anómalo.Contamos una coincidencia cuando una anomalía detectada por Isolation Forest también presenta error en al menos una variable según el modelo LSTM. Este cruce aumenta la confianza en las alertas: si ambos modelos detectan algo raro, es más probable que sea un evento relevante.",
"coincidencias-porcentaje": "% Coincidencia: Refleja qué proporción de las anomalías detectadas por Isolation Forest también fueron respaldadas por el modelo LSTM. Un porcentaje alto sugiere buena coherencia entre modelos y mayor confianza en la detección."
}

def layout2():
 return html.Div([
     # Panel de filtros
     html.Div([
         html.H4("Filtros", style={
             'textAlign': 'center',
             'color': 'white',
             'margin-bottom': '20px',
             'font-weight': 'bold'
         }),
         dbc.Row([
             # Cliente
             dbc.Col(html.Div([
                 html.Small("Seleccione un cliente", style={'color': 'white'}),
                 dcc.Dropdown(
                     id='filtro-cliente',
                     options=[{'label': c, 'value': c} for c in clientes],
                     value=clientes[0],
                     placeholder='Seleccionar Cliente'
                 )
             ], style={'textAlign': 'center'})),
             # Variable
             dbc.Col(html.Div([
                 html.Small("Seleccione una variable", style={'color': 'white'}),
                 dcc.Dropdown(
                     id='filtro-variable',
                     options=[{'label': v, 'value': v} for v in variables],
                     value='Presion',
                     placeholder='Seleccionar Variable'
                 )
             ], style={'textAlign': 'center'})),
             # Fecha
             dbc.Col(html.Div([
                 html.Small("Seleccione un rango de fechas", style={'color': '#white','margin-bottom': '4px'}),
                 dcc.DatePickerRange(
                     id='filtro-fecha',
                     start_date=df_combinado["Fecha"].max() - pd.DateOffset(years=1),
                     end_date=df_combinado["Fecha"].max(),
                     display_format='YYYY-MM-DD'
                 )
             ], style={'display': 'flex', 'flexDirection': 'column','alignItems': 'center'}))
         ], style={'width': '100%'})
     ], style={
         'background-color': '#a0dff7',
         'border-radius': '10px',
         'padding': '20px',
         'margin-bottom': '20px',
         'box-shadow': '0 0 15px rgba(0, 0, 0, 0.2)'
     }),
 
     # Gráfica principal
     html.Div([
         dcc.Graph(id='grafica-linea-tiempo')
     ], style={'margin-bottom': '20px'}),
 
     # Métricas
     html.Div([
         html.H4("Métricas", style={'textAlign': 'center', 'margin-bottom': '20px'}),
         dbc.Row([
             dbc.Col(
                 html.Div([
                     html.H6("RMSE", style={'textAlign': 'center'}),
                     html.P(id="rmse-metrica", style={'textAlign': 'center', 'font-size': '18px'})
                 ], id="card-rmse", style={
                     'background-color': '#f8f9fa', 
                     'border': '1px solid black', 
                     'padding': '10px',
                     'cursor': 'help'
                 })
             ),
             dbc.Col(
                 html.Div([
                     html.H6("MAE", style={'textAlign': 'center'}),
                     html.P(id="mae-metrica", style={'textAlign': 'center', 'font-size': '18px'})
                 ], id="card-mae", style={
                     'background-color': '#f8f9fa', 
                     'border': '1px solid black', 
                     'padding': '10px',
                     'cursor': 'help'
                 })
             ),
             dbc.Col(
                 html.Div([
                     html.H6("Anomalías Filtro", style={'textAlign': 'center'}),
                     html.P(id="anomalias-filtro", style={'textAlign': 'center', 'font-size': '18px'})
                 ], id="card-anomalias-filtro", style={
                     'background-color': '#f8f9fa', 
                     'border': '1px solid black', 
                     'padding': '10px',
                     'cursor': 'help'
                 })
             ),
             dbc.Col(
                 html.Div([
                     html.H6("Anomalías Históricas", style={'textAlign': 'center'}),
                     html.P(id="anomalias-historicas", style={'textAlign': 'center', 'font-size': '18px'})
                 ], id="card-anomalias-historicas", style={
                     'background-color': '#f8f9fa', 
                     'border': '1px solid black', 
                     'padding': '10px',
                     'cursor': 'help'
                 })
             ),
             dbc.Col(
                 html.Div([
                     html.H6("Coincidencias", style={'textAlign': 'center'}),
                     html.P(id="coincidencias", style={'textAlign': 'center', 'font-size': '18px'})
                 ], id="card-coincidencias", style={
                     'background-color': '#f8f9fa', 
                     'border': '1px solid black', 
                     'padding': '10px',
                     'cursor': 'help'
                 })
             ),
             dbc.Col(
                 html.Div([
                     html.H6("Coincidencias %", style={'textAlign': 'center'}),
                     html.P(id="coincidencias-porcentaje", style={'textAlign': 'center', 'font-size': '18px'})
                 ], id="card-coincidencias-porcentaje", style={
                     'background-color': '#f8f9fa', 
                     'border': '1px solid black', 
                     'padding': '10px',
                     'cursor': 'help'
                 })
             ),
         ])
     ], style={'margin-bottom': '20px'}),
 
     # Tooltips para las métricas
     dbc.Tooltip(tooltips["rmse-metrica"], target="card-rmse", placement="top"),
     dbc.Tooltip(tooltips["mae-metrica"], target="card-mae", placement="top"),
     dbc.Tooltip(tooltips["anomalias-filtro"], target="card-anomalias-filtro", placement="top"),
     dbc.Tooltip(tooltips["anomalias-historicas"], target="card-anomalias-historicas", placement="top"),
     dbc.Tooltip(tooltips["coincidencias"], target="card-coincidencias", placement="top"),
     dbc.Tooltip(tooltips["coincidencias-porcentaje"], target="card-coincidencias-porcentaje", placement="top"),
 
     # Análisis de anomalías con botones desplegables y tabla
     dbc.Row([
         # Columna izquierda: Descripción de Score e Histograma
         dbc.Col([
             # Cuadro de texto con descripción de Score y valores estadísticos
             html.Div([
                 html.H6("Acerca del Score de Isolation Forest", style={'textAlign': 'center', 'margin-bottom': '10px'}),
                 html.Div(id='score-stats', style={
                     'background-color': '#f8f9fa',
                     'border': '1px solid #ddd',
                     'border-radius': '5px',
                     'padding': '10px',
                     'margin-bottom': '15px'
                 })
             ]),
             
             # Histograma de scores
             dcc.Graph(id='histograma-scores')
         ], width=6),
         
         # Columna derecha: Botones desplegables y tabla
         dbc.Col([
             # Panel con título y botones desplegables uno al lado del otro
             html.Div([
                 html.H6("¿Qué hacen estos modelos?", style={'textAlign': 'center', 'margin-bottom': '15px'}),
                 
                 # Fila para los botones desplegables
                 dbc.Row([
                     # Botón desplegable para Isolation Forest
                     dbc.Col(
                         dbc.Accordion([
                             dbc.AccordionItem(
                            html.P([
                                "El modelo Isolation Forest detecta anomalías identificando puntos que se desvían significativamente del comportamiento normal. "
                                "Funciona aislando observaciones mediante particiones aleatorias del espacio de características. "
                                "Las anomalías requieren menos particiones para ser aisladas, lo que les asigna un score más alto. ", 
                                html.Strong("El Score en Isolation Forest indica qué tan anómalo es un punto."), 
                                " Valores más negativos indican mayor probabilidad de anomalía. Los puntos normales tienen scores cercanos al promedio, mientras que las anomalías se alejan significativamente. "
                            ], style={'textAlign': 'justify'}),
                            title="Isolation Forest",
                            style={"background-color": "#a0dff7"}
                            ),
                         ], start_collapsed=True),
                         width=6
                     ),
                     
                     # Botón desplegable para LSTM
                     dbc.Col(
                         dbc.Accordion([
                             dbc.AccordionItem(
                                 html.P(
                                     "El modelo LSTM (Long Short-Term Memory) es una red neuronal recurrente especializada en aprender patrones secuenciales. "
                                     "En este caso, predice los valores esperados de presión, temperatura y volumen basándose en datos históricos. "
                                     "Las anomalías se detectan cuando los valores reales se desvían significativamente de las predicciones del modelo.",
                                     style={'textAlign': 'justify'}
                                 ),
                                 title="LSTM",
                                 style={"background-color": "#a0dff7"}
                             ),
                         ], start_collapsed=True),
                         width=6
                     ),
                 ]),
             ], style={'margin-bottom': '20px'}),
             
             # Tabla de anomalías (ahora debajo de los botones desplegables)
             html.Div([
                 html.H6("Últimas 10 anomalías detectadas", style={'textAlign': 'center', 'margin-bottom': '15px'}),
                 html.Div(id='tabla-anomalias')
             ])
         ], width=6)
     ], style={'margin-bottom': '20px'})
 ], style={'background': 'linear-gradient(to bottom, #6ac8e0, #d4f1f9)', 'padding': '20px'})

def register_callbacks_layout2(app):
 @app.callback(
     [
         Output('grafica-linea-tiempo', 'figure'),
         Output('rmse-metrica', 'children'),
         Output('mae-metrica', 'children'),
         Output('anomalias-filtro', 'children'),
         Output('anomalias-historicas', 'children'),
         Output('coincidencias', 'children'),
         Output('coincidencias-porcentaje', 'children'),
         Output('histograma-scores', 'figure'),
         Output('tabla-anomalias', 'children'),
         Output('score-stats', 'children')
     ],
     [
         Input('filtro-cliente', 'value'),
         Input('filtro-variable', 'value'),
         Input('filtro-fecha', 'start_date'),
         Input('filtro-fecha', 'end_date')
     ]
 )
 def actualizar_graficos(cliente, variable, start_date, end_date):
     df_cliente = df_combinado[
         (df_combinado["Client_ID"] == cliente) &
         (df_combinado["Fecha"] >= start_date) &
         (df_combinado["Fecha"] <= end_date)
     ]
 
     # Gráfica de línea
     fig_linea = go.Figure()
     # Actual
     fig_linea.add_trace(go.Scatter(
         x=df_cliente["Fecha"], y=df_cliente[f"{variable}_actual"],
         mode='lines', name='Actual', line=dict(color='#1f77b4')
     ))
     # Predicho
     fig_linea.add_trace(go.Scatter(
         x=df_cliente["Fecha"], y=df_cliente[f"{variable}_predicho"],
         mode='lines', name='Predicho', line=dict(color='#ff7f0e')
     ))
     # Futuro (nuevo)
     col_futuro = f"{variable}_futuro"
     if col_futuro in df_cliente.columns:
         fig_linea.add_trace(go.Scatter(
             x=df_cliente["Fecha"], y=df_cliente[col_futuro],
             mode='lines', name='Futuro', line=dict(color='#067a14', dash='dot')  # Verde claro, línea punteada
         ))
     # Anomalía
     fig_linea.add_trace(go.Scatter(
         x=df_cliente[df_cliente["Anomaly"] == -1]["Fecha"],
         y=df_cliente[df_cliente["Anomaly"] == -1][f"{variable}_actual"],
         mode='markers', name='Anomalía', marker=dict(color='red', symbol='x')
     ))
     fig_linea.update_layout(title=f"{variable} para {cliente} - predicciones LSTM y anomalías")
 
     # Métricas
     rmse = df_errores[(df_errores["Client_ID"] == cliente) & (df_errores["Variable"] == variable)]["RMSE"].values[0]
     mae = df_errores[(df_errores["Client_ID"] == cliente) & (df_errores["Variable"] == variable)]["MAE"].values[0]
     anomalías_filtro = len(df_cliente[df_cliente["Anomaly"] == -1])
     anomalías_historicas = len(df_combinado[(df_combinado["Client_ID"] == cliente) & (df_combinado["Anomaly"] == -1)])
     coincidencias = df_resultados[df_resultados["Client_ID"] == cliente]["Coincidencias con LSTM (cualquier variable)"].values[0]
     
     # Actualizar la fórmula de coincidencia % para que sea Coincidencias / anomalías históricas
     if anomalías_historicas > 0:
         coincidencias_porcentaje = (coincidencias / anomalías_historicas) * 100
     else:
         coincidencias_porcentaje = 0
 
     # Histograma de scores
     fig_scores = px.histogram(df_cliente, x="Score", nbins=50, title=f"Distribución de Scores para {cliente} según Isolation Forest", color_discrete_sequence=["#FFA500"])
     fig_scores.add_vline(x=df_cliente["Score"].mean(), line_dash="dash", line_color="blue", annotation_text="Media")
     fig_scores.add_vline(x=df_cliente["Score"].quantile(0.25), line_dash="dot", line_color="green", annotation_text="Q1")
     fig_scores.add_vline(x=df_cliente["Score"].quantile(0.75), line_dash="dot", line_color="green", annotation_text="Q3")
     
     # Valores estadísticos para el cuadro de texto
     score_mean = df_cliente["Score"].mean()
     score_q1 = df_cliente["Score"].quantile(0.25)
     score_q3 = df_cliente["Score"].quantile(0.75)
     
     # Crear el contenido del cuadro de estadísticas
     score_stats = html.Div([
         html.P([
             html.Strong("Estadísticas de Score:"), 
             html.Br(),
             f"Promedio: {score_mean:.4f}",
             html.Br(),
             f"Q1 (25%): {score_q1:.4f}",
             html.Br(),
             f"Q3 (75%): {score_q3:.4f}"
         ], style={'margin': '0'})
     ])
     
     # Tabla de anomalías - Ahora filtrada por fecha
     # Filtrar las últimas 10 anomalías dentro del rango de fechas seleccionado
     df_anomalias = df_combinado[
         (df_combinado["Client_ID"] == cliente) & 
         (df_combinado["Anomaly"] == -1) &
         (df_combinado["Fecha"] >= start_date) &
         (df_combinado["Fecha"] <= end_date)
     ].sort_values("Fecha", ascending=False).head(10)
     
     # Seleccionar columnas para la tabla
     columnas = ["Fecha", f"{variable}_actual", "Client_ID", "Score"]
     df_tabla = df_anomalias[columnas].copy()
     df_tabla.columns = ["Fecha", variable, "Cliente", "Score"]
     
     # Formatear la fecha para mejor visualización
     df_tabla["Fecha"] = df_tabla["Fecha"].dt.strftime('%Y-%m-%d %H:%M')
     
     # Formatear los valores numéricos
     df_tabla[variable] = df_tabla[variable].round(2)
     df_tabla["Score"] = df_tabla["Score"].round(4)
     
     # Crear la tabla
     tabla = dash_table.DataTable(
         id='tabla-anomalias-data',
         columns=[{"name": i, "id": i} for i in df_tabla.columns],
         data=df_tabla.to_dict('records'),
         style_header={
             'backgroundColor': '#1e3d59',
             'color': 'white',
             'fontWeight': 'bold',
             'textAlign': 'center'
         },
         style_cell={
             'textAlign': 'center',
             'padding': '10px',
             'border': '1px solid grey'
         },
         style_data_conditional=[
             {
                 'if': {'row_index': 'odd'},
                 'backgroundColor': '#f2f2f2'
             }
         ]
     )
 
     return fig_linea, f"{rmse:.2f}", f"{mae:.2f}", anomalías_filtro, anomalías_historicas, coincidencias, f"{coincidencias_porcentaje:.2f}%", fig_scores, tabla, score_stats