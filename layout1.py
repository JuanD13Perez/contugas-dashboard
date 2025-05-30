
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Cargar datos
full_df = pd.read_csv("data/Datos_Contugas_Compacted.csv", parse_dates=["Fecha"])

# Opciones para el filtro de agregación
AGG_OPTIONS = {
    'Hora': 'hour',
    'Fecha': 'day',
    'Semana': 'week',
    'Mes': 'month',
    'Trimestre': 'quarter'
}

def layout1():
    clientes = full_df['ClientId'].unique()

    return html.Div([
        # Panel de filtros con título y animación
        html.Div([
            html.H4("Filtros", style={
                'textAlign': 'center',
                'color': 'white',
                'margin-bottom': '20px',
                'font-weight': 'bold'
            }),
            dbc.Row([
                # Filtro de rango de fechas
                dbc.Col(html.Div([
                    html.Small("Seleccione un rango de fechas", style={'color': 'white','margin-bottom': '4px'}),
                    dcc.DatePickerRange(
                        id='filtro-fecha',
                        min_date_allowed=full_df['Fecha'].min().date(),
                        max_date_allowed=full_df['Fecha'].max().date(),
                        start_date=full_df['Fecha'].min().date(),
                        end_date=full_df['Fecha'].max().date(),
                        display_format='YYYY-MM-DD'
                    )
                ], style={ 'display': 'flex', 'flexDirection': 'column','alignItems': 'center'})),
                # Filtro de cliente
                dbc.Col(html.Div([
                    html.Small("Seleccione un cliente", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='filtro-cliente',
                        options=[{'label': c, 'value': c} for c in clientes],
                        value=clientes[0],
                        placeholder='Seleccionar Cliente'
                    )
                ], style={'textAlign': 'center'})),
                # Filtro de tipo de agregación
                dbc.Col(html.Div([
                    html.Small("Seleccione un tipo de agregación", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='filtro-tipo',
                        options=[{'label': k, 'value': v} for k, v in AGG_OPTIONS.items()],
                        value='day'
                    )
                ], style={'textAlign': 'center'}))
            ], style={'width': '100%'})
        ], style={
            'background-color': '#a0dff7',
            'border-radius': '10px',
            'padding': '20px',
            'margin-bottom': '20px',
            'position': 'relative',
            'box-shadow': '0 0 15px rgba(0, 0, 0, 0.2)'
        }, className="animated-border"),

        # Panel de histogramas
        dbc.Row([
            dbc.Col(dcc.Graph(id='hist-presion', style={'border': '2px solid #2c3e50', 'border-radius': '8px'}), width=4),
            dbc.Col(dcc.Graph(id='hist-temperatura', style={'border': '2px solid #2c3e50', 'border-radius': '8px'}), width=4),
            dbc.Col(dcc.Graph(id='hist-volumen', style={'border': '2px solid #2c3e50', 'border-radius': '8px'}), width=4),
        ]),

        # Panel de líneas de tiempo
        dbc.Row([
            dbc.Col(dcc.Graph(id='serie-presion', style={'border': '2px solid #2c3e50', 'border-radius': '8px'}), width=12),
            dbc.Col(dcc.Graph(id='serie-temperatura', style={'border': '2px solid #2c3e50', 'border-radius': '8px'}), width=12),
            dbc.Col(dcc.Graph(id='serie-volumen', style={'border': '2px solid #2c3e50', 'border-radius': '8px'}), width=12),
        ])
    ], style={'background': 'linear-gradient(to bottom, #6ac8e0, #d4f1f9)', 'padding': '20px'})

def agregar_datos(df, tipo):
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df = df.set_index('Fecha')
    if tipo == 'hour':
        grouped = df.resample('H').mean().reset_index()
    elif tipo == 'day':
        grouped = df.resample('D').mean().reset_index()
    elif tipo == 'week':
        grouped = df.resample('W-MON').mean().reset_index()
    elif tipo == 'month':
        grouped = df.resample('M').mean().reset_index()
    elif tipo == 'quarter':
        grouped = df.resample('Q').mean().reset_index()
    else:
        grouped = df.reset_index()
    return grouped

def resumen_estadistico(series):
    stats = {
        'Media': series.mean(),
        'Desviación': series.std(),
        'Q1': series.quantile(0.25),
        'Q2': series.median(),
        'Q3': series.quantile(0.75),
        'Mínimo': series.min(),
        'Máximo': series.max()
    }
    texto = '<br>'.join([f'{k}: {v:.2f}' for k, v in stats.items()])
    return texto

def crear_histograma(df, columna):
    color = {'Presion': '#FFD700', 'Temperatura': '#87CEFA', 'Volumen': '#FFA500'}.get(columna, 'blue')
    fig = px.histogram(df, x=columna, nbins=30, title=f'Histograma de {columna}', color_discrete_sequence=[color])
    stats = resumen_estadistico(df[columna])
    fig.add_annotation(
        text=stats,
        xref="paper",
        yref="paper",
        x=1,
        y=1,
        showarrow=False,
        align='left',
        font=dict(size=12, color="black"),
        bordercolor="black",
        borderwidth=1,
        bgcolor="white",
        opacity=0.8,
        xanchor='right',   # <- Ancla el borde derecho del texto a x=1
        yanchor='top'

    )
    return fig

def crear_linea(df, columna, tipo):
    mean_value = df[columna].mean()
    std_dev = df[columna].std()
    fig = px.line(df, x='Fecha', y=columna, title=f'{columna} a lo largo del tiempo ({tipo})', color_discrete_sequence=['#2E8B57'])
    fig.add_trace(go.Scatter(x=df['Fecha'], y=[mean_value] * len(df), mode='lines', name='Promedio', line=dict(color='lightgreen', dash='dash')))
    fig.add_trace(go.Scatter(x=df['Fecha'], y=[mean_value + 2 * std_dev] * len(df), mode='lines', name='+2σ', line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=df['Fecha'], y=[mean_value - 2 * std_dev] * len(df), mode='lines', name='-2σ', line=dict(color='red', dash='dot')))
    stats_text = f"Promedio: {mean_value:.2f} | +2σ: {mean_value + 2 * std_dev:.2f} | -2σ: {mean_value - 2 * std_dev:.2f}"
    fig.add_annotation(
        text=stats_text,
        xref="paper",
        yref="paper",
        x=0.95,
        y=0.95,
        showarrow=False,
        align='right',
        font=dict(size=12, color="black"),
        bordercolor="black",
        borderwidth=1,
        bgcolor="white",
        opacity=0.8
    )
    return fig

def register_callbacks_hist(app):
    @app.callback(
        [
            Output('hist-presion', 'figure'),
            Output('hist-temperatura', 'figure'),
            Output('hist-volumen', 'figure'),
            Output('serie-presion', 'figure'),
            Output('serie-temperatura', 'figure'),
            Output('serie-volumen', 'figure'),
        ],
        [
            Input('filtro-fecha', 'start_date'),
            Input('filtro-fecha', 'end_date'),
            Input('filtro-cliente', 'value'),
            Input('filtro-tipo', 'value'),
        ]
    )
    def actualizar_graficos(start_date, end_date, cliente, tipo):
        dff = full_df[(full_df['ClientId'] == cliente) & (full_df['Fecha'] >= start_date) & (full_df['Fecha'] <= end_date)]
        df_agg = agregar_datos(dff[['Fecha', 'Presion', 'Temperatura', 'Volumen']].copy(), tipo)
        return (
            crear_histograma(dff, 'Presion'),
            crear_histograma(dff, 'Temperatura'),
            crear_histograma(dff, 'Volumen'),
            crear_linea(df_agg, 'Presion', tipo),
            crear_linea(df_agg, 'Temperatura', tipo),
            crear_linea(df_agg, 'Volumen', tipo),
        )
