from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import requests
from datetime import datetime
import os
# URL de la API
API_URL = os.environ.get("API_URL", "http://localhost:8000")
## URL de la API
#API_URL = "http://localhost:8000"  # Cambiar según donde esté desplegada la API

def layout3():
    return html.Div([
        # Panel de carga de archivo
        html.Div([
            html.H4("Carga de datos para predicción", style={
                'textAlign': 'center',
                'color': 'white',
                'margin-bottom': '20px',
                'font-weight': 'bold'
            }),
            dbc.Row([
                dbc.Col([
                    html.P("Sube un archivo Excel con datos para predecir:", style={'color': 'white'}),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Arrastra o ',
                            html.A('selecciona un archivo', style={'color': '#ffcc00', 'text-decoration': 'underline'})
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px 0',
                            'background': 'rgba(255, 255, 255, 0.2)',
                            'color': 'white'
                        },
                        multiple=False
                    ),
                    html.Div(id='upload-output', style={'color': 'white', 'margin-top': '10px'})
                ], width=6),
                
                dbc.Col([
                    html.P("Requisitos del archivo:", style={'color': 'white', 'font-weight': 'bold'}),
                    html.Ul([
                        html.Li("Formato Excel (.xlsx)"),
                        html.Li("Columnas requeridas: Fecha, Presion, Temperatura, Volumen, Client_ID"),
                        html.Li("Fecha debe ser para 2024-01-01"),
                        html.Li("Debe contener las 24 horas del día")
                    ], style={'color': 'white', 'padding-left': '20px'})
                ], width=6)
            ])
        ], style={
            'background-color': '#a0dff7',
            'border-radius': '10px',
            'padding': '20px',
            'margin-bottom': '20px',
            'box-shadow': '0 0 15px rgba(0, 0, 0, 0.2)'
        }),
        
        # Panel de prueba de conexión API
        html.Div([
            html.H4("Prueba de conexión con la API", style={'textAlign': 'center', 'margin-bottom': '15px'}),
            dbc.Row([
                dbc.Col([
                    html.Button("Probar conexión API", id="test-api-button", style={
                        'margin': '10px',
                        'background-color': '#57a63a',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 15px',
                        'border-radius': '5px'
                    }),
                    dbc.Spinner(
                        html.Div(id="api-test-result", style={'margin': '10px', 'min-height': '50px'})
                    )
                ], width=12)
            ])
        ], style={
            'background-color': '#ffffff',
            'border-radius': '10px',
            'padding': '20px',
            'margin-bottom': '20px',
            'box-shadow': '0 0 10px rgba(0, 0, 0, 0.1)'
        }),
        
        # Panel de selección de cliente
        html.Div([
            html.H4("Selección de cliente", style={'textAlign': 'center', 'margin-bottom': '15px'}),
            dbc.Row([
                dbc.Col([
                    html.P("Seleccione un cliente para visualizar predicciones:"),
                    dcc.Dropdown(
                        id='cliente-dropdown',
                        options=[],
                        placeholder='Seleccione un cliente...',
                        disabled=True
                    )
                ], width=6),
                dbc.Col([
                    html.Div(id='modelo-info', style={'padding': '10px', 'background': '#f8f9fa', 'border-radius': '5px'})
                ], width=6)
            ])
        ], style={
            'background-color': '#ffffff',
            'border-radius': '10px',
            'padding': '20px',
            'margin-bottom': '20px',
            'box-shadow': '0 0 10px rgba(0, 0, 0, 0.1)'
        }),
        
        # Panel de visualización de datos y predicciones
        dbc.Row([
            # Gráficas
            dbc.Col([
                html.H4("Visualización de predicciones", style={'textAlign': 'center', 'margin-bottom': '15px'}),
                dcc.Graph(id='grafica-predicciones')
            ], width=8),
            
            # Tabla de datos
            dbc.Col([
                html.H4("Datos de predicción", style={'textAlign': 'center', 'margin-bottom': '15px'}),
                html.Div(id='tabla-predicciones')
            ], width=4)
        ], style={'margin-bottom': '20px'}),
        
        # Panel de información
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Acerca del modelo LSTM", style={'textAlign': 'center', 'margin-bottom': '10px'}),
                    html.P([
                        "El modelo LSTM (Long Short-Term Memory) utilizado para estas predicciones ha sido entrenado con datos históricos de cada cliente. ",
                        "Utiliza una ventana de 24 horas para predecir los valores de las próximas 24 horas. ",
                        html.Strong("Las predicciones son más precisas cuando los datos de entrada siguen patrones similares a los datos de entrenamiento.")
                    ], style={'textAlign': 'justify'})
                ], style={
                    'background-color': '#f8f9fa',
                    'border-radius': '10px',
                    'padding': '20px',
                    'box-shadow': '0 0 10px rgba(0, 0, 0, 0.1)'
                })
            ], width=12)
        ]),
        
        # Almacenamiento de datos
        dcc.Store(id='stored-data')
    ], style={'background': 'linear-gradient(to bottom, #6ac8e0, #d4f1f9)', 'padding': '20px'})

def parse_contents(contents, filename):
    """Procesa el contenido del archivo subido"""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'xlsx' in filename:
            # Leer archivo Excel
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "Por favor, sube un archivo Excel (.xlsx)"
        
        # Verificar columnas requeridas
        required_cols = ["Fecha", "Presion", "Temperatura", "Volumen", "Client_ID"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return None, f"Faltan columnas requeridas: {', '.join(missing_cols)}"
        
        # Convertir Fecha a datetime si no lo es
        if not pd.api.types.is_datetime64_any_dtype(df["Fecha"]):
            try:
                df["Fecha"] = pd.to_datetime(df["Fecha"])
            except:
                return None, "Error al convertir la columna Fecha a formato datetime"
        
        # Verificar que los datos son para 2024-01-01
        fechas_unicas = df["Fecha"].dt.date.unique()
        if len(fechas_unicas) != 1 or fechas_unicas[0] != datetime(2024, 1, 1).date():
            return None, "Los datos deben ser para la fecha 2024-01-01"
        
        # Verificar que hay 24 horas para cada cliente
        clientes = df["Client_ID"].unique()
        for cliente in clientes:
            horas_cliente = df[df["Client_ID"] == cliente]["Fecha"].dt.hour.nunique()
            if horas_cliente != 24:
                return None, f"El cliente {cliente} no tiene datos para las 24 horas del día"
        
        return df, f"Archivo cargado correctamente. {len(clientes)} clientes encontrados."
    
    except Exception as e:
        return None, f"Error al procesar el archivo: {str(e)}"

def register_callbacks_layout3(app):
    # Callback para probar la conexión con la API
    @app.callback(
        Output("api-test-result", "children"),
        Input("test-api-button", "n_clicks"),
        prevent_initial_call=True
    )
    def test_api_connection(n_clicks):
        if n_clicks:
            try:
                response = requests.get(f"{API_URL}")
                if response.status_code == 200:
                    # Obtener lista de clientes disponibles
                    try:
                        clients_response = requests.get(f"{API_URL}/clients")
                        if clients_response.status_code == 200:
                            clients = clients_response.json().get("clients", [])
                            return html.Div([
                                html.P("✅ Conexión exitosa con la API", style={'color': 'green', 'font-weight': 'bold'}),
                                html.P(f"Respuesta: {response.json()}"),
                                html.P(f"Clientes disponibles: {len(clients)}", style={'margin-top': '10px'}),
                                html.Ul([html.Li(f"Cliente {c}") for c in clients[:5]] + 
                                       ([html.Li("...")] if len(clients) > 5 else []))
                            ])
                        else:
                            return html.Div([
                                html.P("✅ Conexión exitosa con la API", style={'color': 'green', 'font-weight': 'bold'}),
                                html.P(f"Respuesta: {response.json()}"),
                                html.P(f"Error al obtener clientes: {clients_response.status_code}", style={'color': 'orange'})
                            ])
                    except Exception as e:
                        return html.Div([
                            html.P("✅ Conexión exitosa con la API", style={'color': 'green', 'font-weight': 'bold'}),
                            html.P(f"Respuesta: {response.json()}"),
                            html.P(f"Error al obtener clientes: {str(e)}", style={'color': 'orange'})
                        ])
                else:
                    return html.P(f"❌ Error: {response.status_code} - {response.text}", style={'color': 'red'})
            except Exception as e:
                return html.P(f"❌ Error de conexión: {str(e)}", style={'color': 'red'})

    @app.callback(
        [
            Output('upload-output', 'children'),
            Output('cliente-dropdown', 'options'),
            Output('cliente-dropdown', 'disabled'),
            Output('cliente-dropdown', 'value'),
            Output('stored-data', 'data')
        ],
        Input('upload-data', 'contents'),
        State('upload-data', 'filename')
    )
    def update_output(contents, filename):
        if contents is None:
            return "Ningún archivo seleccionado", [], True, None, None
        
        # Procesar el archivo
        df, mensaje = parse_contents(contents, filename)
        
        if df is None:
            return mensaje, [], True, None, None
        
        # Obtener clientes disponibles
        clientes = df["Client_ID"].unique()
        opciones = [{'label': f"Cliente {c}", 'value': c} for c in clientes]
        
        # Verificar qué clientes tienen modelos disponibles en la API
        try:
            response = requests.get(f"{API_URL}/clients", timeout=5)
            if response.status_code == 200:
                clientes_api = response.json()["clients"]
                opciones = [{'label': f"Cliente {c}", 'value': c} for c in clientes if c in clientes_api]
                
                if not opciones:
                    return f"{mensaje} Pero ninguno tiene modelo disponible en la API.", [], True, None, None
        except Exception as e:
            # Si hay error al conectar con la API, mostramos un mensaje pero seguimos con todos los clientes
            mensaje += f" (Advertencia: No se pudo verificar disponibilidad de modelos en la API: {str(e)})"
        
        # Guardar datos en formato JSON para dcc.Store
        df_json = df.to_json(date_format='iso', orient='split')
        
        return mensaje, opciones, False, None, df_json

    @app.callback(
        [
            Output('modelo-info', 'children'),
            Output('grafica-predicciones', 'figure'),
            Output('tabla-predicciones', 'children')
        ],
        Input('cliente-dropdown', 'value'),
        State('stored-data', 'data')
    )
    def update_predicciones(cliente_id, stored_data):
        if cliente_id is None or stored_data is None:
            return "Seleccione un cliente para ver información del modelo", go.Figure(), None
        
        # Recuperar datos del dcc.Store
        df = pd.read_json(stored_data, orient='split')
        df_cliente = df[df["Client_ID"] == cliente_id]
        
        # Preparar datos para enviar a la API
        data_to_send = {
            "client_id": cliente_id,
            "data": df_cliente.to_dict('records')
        }
        
        try:
            # Obtener datos históricos y estadísticas de anomalías
            historical_response = requests.get(
                f"{API_URL}/historical-data/{cliente_id}",
                timeout=30
            )
            
            if historical_response.status_code != 200:
                historical_data = None
                anomaly_stats = None
            else:
                historical_result = historical_response.json()
                historical_data = historical_result.get("historical_data", [])
                anomaly_count = historical_result.get("anomaly_count", 0)
                anomaly_averages = historical_result.get("anomaly_averages", {})
                
                # Crear componente para mostrar estadísticas de anomalías
                anomaly_stats = html.Div([
                    html.H5("Estadísticas de Anomalías (Último Mes)", style={
                        'textAlign': 'center', 
                        'margin-top': '20px',
                        'margin-bottom': '15px',
                        'color': '#1e3d59',
                        'font-weight': 'bold'
                    }),
                    html.Div([
                        html.Div([
                            html.H6("Número de Anomalías", style={'textAlign': 'center', 'color': '#1e3d59'}),
                            html.P(f"{anomaly_count}", style={
                                'textAlign': 'center', 
                                'font-size': '24px', 
                                'font-weight': 'bold',
                                'color': '#d62728' if anomaly_count > 0 else '#2ca02c'
                            })
                        ], style={
                            'flex': '1', 
                            'padding': '15px', 
                            'background': '#f8f9fa', 
                            'border-radius': '5px', 
                            'margin': '5px',
                            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
                        }),
                        html.Div([
                            html.H6("Promedios en Anomalías", style={'textAlign': 'center', 'color': '#1e3d59'}),
                            html.Table([
                                html.Thead(html.Tr([
                                    html.Th("Variable", style={'padding': '8px', 'border-bottom': '2px solid #ddd', 'text-align': 'left'}), 
                                    html.Th("Valor", style={'padding': '8px', 'border-bottom': '2px solid #ddd', 'text-align': 'right'})
                                ])),
                                html.Tbody([
                                    html.Tr([
                                        html.Td("Presión", style={'padding': '8px', 'border-bottom': '1px solid #ddd'}), 
                                        html.Td(f"{anomaly_averages.get('Presion', 'N/A'):.2f}", style={'padding': '8px', 'border-bottom': '1px solid #ddd', 'text-align': 'right'})
                                    ]) if 'Presion' in anomaly_averages else None,
                                    html.Tr([
                                        html.Td("Temperatura", style={'padding': '8px', 'border-bottom': '1px solid #ddd'}), 
                                        html.Td(f"{anomaly_averages.get('Temperatura', 'N/A'):.2f}", style={'padding': '8px', 'border-bottom': '1px solid #ddd', 'text-align': 'right'})
                                    ]) if 'Temperatura' in anomaly_averages else None,
                                    html.Tr([
                                        html.Td("Volumen", style={'padding': '8px', 'border-bottom': '1px solid #ddd'}), 
                                        html.Td(f"{anomaly_averages.get('Volumen', 'N/A'):.2f}", style={'padding': '8px', 'border-bottom': '1px solid #ddd', 'text-align': 'right'})
                                    ]) if 'Volumen' in anomaly_averages else None,
                                ])
                            ], style={'width': '100%', 'border-collapse': 'collapse'})
                        ], style={
                            'flex': '2', 
                            'padding': '15px', 
                            'background': '#f8f9fa', 
                            'border-radius': '5px', 
                            'margin': '5px',
                            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'display': 'flex', 'margin-top': '10px'})
                ])
            
            # Llamar a la API para obtener predicciones
            response = requests.post(
                f"{API_URL}/predict",
                json=data_to_send,
                timeout=30
            )
            
            if response.status_code != 200:
                info_modelo = html.Div([
                    html.H6("Error en la API", style={'color': 'red'}),
                    html.P(f"Error {response.status_code}: {response.json().get('detail', 'Error desconocido')}")
                ])
                return info_modelo, go.Figure(), None
            
            # Procesar respuesta
            result = response.json()
            
            # Información del modelo
            info_modelo = html.Div([
                html.H6(f"Modelo LSTM para Cliente {cliente_id}", style={'color': 'green'}),
                html.P(f"Ventana de predicción: 24 horas"),
                html.P(f"Predicciones futuras: 24 horas"),
                html.P(f"Estado: {result['message']}")
            ])
            
            # Crear figura para las predicciones
            fig = go.Figure()
            
            # Variables y colores
            variables = ["Presion", "Temperatura", "Volumen"]
            colores = {
                "real": {"Presion": "#1f77b4", "Temperatura": "#ff7f0e", "Volumen": "#2ca02c"},
                "historico": {"Presion": "#17becf", "Temperatura": "#bcbd22", "Volumen": "#7f7f7f"},
                "predicho": {"Presion": "#aec7e8", "Temperatura": "#ffbb78", "Volumen": "#98df8a"},
                "futuro": {"Presion": "#d62728", "Temperatura": "#9467bd", "Volumen": "#8c564b"}
            }
            
            # Añadir datos históricos si están disponibles
            if historical_data:
                df_hist = pd.DataFrame(historical_data)
                df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"])
                
                # Añadir datos históricos
                for var in variables:
                    fig.add_trace(go.Scatter(
                        x=df_hist["Fecha"],
                        y=df_hist[var],
                        mode='lines',
                        name=f'{var} Histórico',
                        line=dict(color=colores["historico"][var])
                    ))
                
                # Añadir anomalías como puntos
                df_anomalias = df_hist[df_hist["Anomaly"] == -1]
                if not df_anomalias.empty:
                    for var in variables:
                        fig.add_trace(go.Scatter(
                            x=df_anomalias["Fecha"],
                            y=df_anomalias[var],
                            mode='markers',
                            name=f'Anomalías {var}',
                            marker=dict(color='red', symbol='x', size=10)
                        ))
            
            # Añadir datos reales del archivo cargado
            for var in variables:
                fig.add_trace(go.Scatter(
                    x=df_cliente["Fecha"],
                    y=df_cliente[var],
                    mode='lines',
                    name=f'{var} Cargado',
                    line=dict(color=colores["real"][var])
                ))
            
            # Añadir predicciones sobre datos existentes
            if result['predictions']:
                fechas_pred = [datetime.fromisoformat(p["Fecha"]) for p in result['predictions']]
                for i, var in enumerate(variables):
                    fig.add_trace(go.Scatter(
                        x=fechas_pred,
                        y=[p[var] for p in result['predictions']],
                        mode='lines',
                        name=f'{var} Predicho',
                        line=dict(color=colores["predicho"][var], dash='dash')
                    ))
            
            # Añadir predicciones futuras
            fechas_futuro = [datetime.fromisoformat(p["Fecha"]) for p in result['future_predictions']]
            for var in variables:
                fig.add_trace(go.Scatter(
                    x=fechas_futuro,
                    y=[p[var] for p in result['future_predictions']],
                    mode='lines',
                    name=f'{var} Futuro',
                    line=dict(color=colores["futuro"][var], dash='dot')
                ))
            
            fig.update_layout(
                title=f'Predicciones para Cliente {cliente_id}',
                xaxis_title='Fecha',
                yaxis_title='Valor',
                legend_title='Variables',
                height=600
            )
            
            # Crear tabla de predicciones futuras
            df_predicciones = pd.DataFrame(result['future_predictions'])
            df_predicciones["Fecha"] = pd.to_datetime(df_predicciones["Fecha"])
            # Redondear todas las columnas numéricas a 2 decimales
            for col in df_predicciones.columns:
             if col != "Fecha":
                 df_predicciones[col] = df_predicciones[col].round(2)
            
            tabla = html.Div([
                dash_table.DataTable(
                    id='tabla-datos-predicciones',
                    columns=[{"name": i, "id": i} for i in df_predicciones.columns],
                    data=df_predicciones.to_dict('records'),
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
                    ],
                    page_size=10
                ),
                
                # Añadir estadísticas de anomalías debajo de la tabla
                anomaly_stats if anomaly_stats else html.Div()
            ])
            
            return info_modelo, fig, tabla
            
        except Exception as e:
            info_modelo = html.Div([
                html.H6("Error de conexión", style={'color': 'red'}),
                html.P(f"No se pudo conectar con la API: {str(e)}")
            ])
            return info_modelo, go.Figure(), None