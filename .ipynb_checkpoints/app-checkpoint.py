import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from layout1 import layout1, register_callbacks_hist
from layout2 import layout2, register_callbacks_layout2
from layout3 import layout3, register_callbacks_layout3  # Importar layout3 y sus callbacks

# Inicializar app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "Contugas - Dashboard"
server = app.server

# Cargar datos
df = pd.read_csv("Data/Datos_Contugas_Compacted.csv", parse_dates=["Fecha"])

# Diccionario de rutas a etiquetas
routes = {
 "/": "hist",
 "/anomalies": "anom",
 "/modeling": "model"
}

# Función para construir botones con estilos dinámicos
def nav_buttons(active_page):
 def get_style(key):
     return {
         'margin': '5px',
         'background-color': '#57a63a' if active_page == key else '#92a892',
         'color': 'white',
         'border': 'none',
         'height': '40px',
         'padding': '0 12px',
         'font-size': '14px',
         'font-weight': 'bold',
         'border-radius': '5px',
         'cursor': 'pointer',
         'white-space': 'nowrap',
         'overflow': 'hidden',
         'text-overflow': 'ellipsis'
     }

 return html.Div([
     dcc.Link(html.Button("Análisis Histórico", id="btn-hist", style=get_style("hist")), href="/"),
     dcc.Link(html.Button("Detección de Anomalías", id="btn-anom", style=get_style("anom")), href="/anomalies"),
     dcc.Link(html.Button("Modelamiento", id="btn-model", style=get_style("model")), href="/modeling")
 ], style={
     'flex': '1',
     'display': 'flex',
     'justify-content': 'space-evenly',
     'align-items': 'center'
 })

# Registrar callbacks de todos los layouts
register_callbacks_hist(app)
register_callbacks_layout2(app)
register_callbacks_layout3(app)  # Registrar callbacks de layout3

# Layout general con routing
app.layout = html.Div([
 dcc.Location(id='url', refresh=False),

 html.Div([
     html.Div([
         # Aumentar el tamaño de la imagen del banner
         html.Img(src="assets/ContugasBanner.png", style={
             'height': '160px',  # Aumentado de 120px a 150px
             'object-fit': 'contain', 
             'margin': '10px'
         })
     ], style={'flex': '1', 'width': '25%', 'display': 'flex', 'align-items': 'center'}),

     html.Div([
         html.H1("Dashboard de Mediciones de Gas – Contugas", style={
             'textAlign': 'center',
             'color': '#57a63a',
             'font-size': '36px',
             'font-family': 'Arial Black',
             'font-weight': 'bold',
             'margin': '0'
         })
     ], style={'flex': '1', 'width': '50%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

     html.Div(id="nav-buttons-container", style={
         'flex': '1',
         'width': '25%',
         'display': 'flex',
         'align-items': 'center',
         'justify-content': 'center'
     })
 ], style={
     'display': 'flex',
     'flex-direction': 'row',
     'background': 'linear-gradient(to right, #b7e4a6, #e0f3d1)',
     'padding': '10px',
     'border-radius': '8px',
     'margin-bottom': '20px'
 }),

 html.Div(id='layout-container'),

 # Línea morada con dos imágenes a la izquierda
 html.Div([
     # Contenedor para las imágenes
     html.Div([
         html.Img(src="assets/uniandes.png", style={
             'height': '70px',
             'margin-right': '25px',
             'object-fit': 'contain'
         }),
         html.Img(src="assets/MIAD.png", style={
             'height': '60px',
             'object-fit': 'contain'
         })
     ], style={
         'display': 'flex',
         'align-items': 'center',
         'margin-left': '20px'
     }),
     
     # Espacio vacío para mantener el diseño
     html.Div(style={'flex': '1'})
 ], style={
     'width': '100%',
     'height': '7vh',
     'background': 'linear-gradient(to right, #434584, #773e81)',
     'z-index': '9999',
     'display': 'flex',
     'align-items': 'center'
 })
])

@app.callback(
 [Output('layout-container', 'children'), Output('nav-buttons-container', 'children')],
 Input('url', 'pathname')
)
def display_page(pathname):
 page_key = routes.get(pathname, "hist")

 if page_key == "hist":
     content = layout1()
 elif page_key == "anom":
     content = layout2()
 elif page_key == "model":
     content = layout3()  # Usar layout3() en lugar del div temporal
 else:
     content = html.Div([html.H4("Página no encontrada")])

 nav_buttons_updated = nav_buttons(page_key)

 return content, nav_buttons_updated

if __name__ == '__main__':
 app.run(debug=True)