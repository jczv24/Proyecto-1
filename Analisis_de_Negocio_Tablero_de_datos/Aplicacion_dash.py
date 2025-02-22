import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px 
import pandas as pd

# Cargar datos
df = pd.read_csv('datos_limpios.csv', encoding_errors='replace', delimiter=',')
estados_unicos = sorted(df['state'].unique())

# Inicializar app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
app.config.suppress_callback_exceptions = True
# Layout del tablero con pestañas
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Análisis de Datos', value='tab1'),
        dcc.Tab(label='Predicción', value='tab2')
    ]),
    html.Div(id='tabs-content')
])

# Contenido de las pestañas
@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_tab_content(tab):
    if tab == 'tab1':
        return html.Div([
            html.H1('Arrendamiento de Apartamentos', style={'textAlign': 'center'}),
            
            # Filtros
            html.Div([
                html.Div([
                    html.Label('Estado:'),
                    dcc.Dropdown(
                        id='ciudad-filtro',
                        options=[{'label': estado, 'value': estado} for estado in df['state'].dropna().unique()],
                        value=None,
                        placeholder='Selecciona un estado',
                        multi=True
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

                html.Div([
                    html.Label('Número de habitaciones:'),
                    dcc.Dropdown(
                        id='habitaciones-filtro',
                        options=[{'label': str(hab), 'value': hab} for hab in sorted(df['bedrooms'].dropna().unique())],
                        value=None,
                        placeholder='Selecciona número de habitaciones',
                        multi=True
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
            ], style={'display': 'flex', 'justify-content': 'space-between', 'padding': '10px'}),

            # Estadísticas
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("Precio Promedio", className="card-title", style={'textAlign': 'center'}),
                    html.P(id='precio-promedio', className="card-text", style={'textAlign': 'center'})
                ]), color="dark", inverse=True), width=4),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("Precio (Mediana)", className="card-title", style={'textAlign': 'center'}),
                    html.P(id='precio-mediano', className="card-text", style={'textAlign': 'center'})
                ]), color="dark", inverse=True), width=4),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("Desviación Estándar", className="card-title", style={'textAlign': 'center'}),
                    html.P(id='desviacion-estandar', className="card-text", style={'textAlign': 'center'})
                ]), color="dark", inverse=True), width=4)
            ], style={'padding': '20px'}),

            # Gráficos
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4('Distribución de Precios', style={'textAlign': 'center'}),
                    dcc.Graph(id='histograma-precios')
                ])), width=6),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4('Precio vs Tamaño (ft²)', style={'textAlign': 'center'}),
                    dcc.Graph(id='dispersion-precio-tamano')
                ])), width=6)
            ]),

            dbc.Card(dbc.CardBody([
                html.H4('Precio Promedio por Estado', style={'textAlign': 'center'}),
                dcc.Graph(id='mapa-precios')
            ]))
        ])
    elif tab == 'tab2':
        return html.Div([
            
            html.H1("Predicción del Precio de Apartamentos"),

    # Entradas del formulario
    html.Div([
        html.Label("Número de baños:"),
        dcc.Input(id='input-bathrooms', type='number', value=1, min=0),

        html.Label("Número de habitaciones:"),
        dcc.Input(id='input-bedrooms', type='number', value=1, min=0),

        html.Label("Metros cuadrados:"),
        dcc.Input(id='input-square_feet', type='number', value=50, min=10),

        html.Label("Estado:"),
        dcc.Dropdown(
            id='input-state',
            options=[{'label': estado, 'value': estado} for estado in estados_unicos],
            value=estados_unicos[0]
        ),

        html.Label("Ciudad:"),
        dcc.Dropdown(id='input-cityname', options=[], value=None),

        html.Label("Permite mascotas (Cats, Dogs, None):"),
        dcc.Input(id='input-pets_allowed', type='text', value='Cats,Dogs'),

        html.Label("Fuente (RentLingo, Zillow, etc.):"),
        dcc.Input(id='input-source', type='text', value='RentLingo'),

        html.Label("Latitud:"),
        dcc.Input(id='input-latitude', type='number', value=29.7714),

        html.Label("Longitud:"),
        dcc.Input(id='input-longitude', type='number', value=-95.4343),

        html.Label("Conteo del cuerpo del anuncio:"),
        dcc.Input(id='input-body_count', type='number', value=100, min=0),
    ], style={'display': 'grid', 'grid-template-columns': '1fr', 'gap': '10px'}),

    html.Br(),
    html.Button('Predecir Precio', id='predict-button', n_clicks=0),
    html.Br(), html.Br(),

    # Salida de la predicción
    html.Div(id='output-prediction')
            
        ])
        
# Callback para actualizar las ciudades según el estado
@app.callback(
    Output('input-cityname', 'options'),
    Input('input-state', 'value')
)
def update_cities(selected_state):
    ciudades = sorted(df[df['state'] == selected_state]['cityname'].unique())
    return [{'label': ciudad, 'value': ciudad} for ciudad in ciudades]

# Callbacks para actualizar gráficos y estadísticas
@app.callback(
    [Output('histograma-precios', 'figure'),
     Output('dispersion-precio-tamano', 'figure'),
     Output('mapa-precios', 'figure'),
     Output('precio-promedio', 'children'),
     Output('precio-mediano', 'children'),
     Output('desviacion-estandar', 'children')],
    [Input('ciudad-filtro', 'value'),
     Input('habitaciones-filtro', 'value')]
)
def actualizar_graficos(estados, habitaciones):
    df_filtrado = df.copy()
    if estados:
        df_filtrado = df_filtrado[df_filtrado['state'].isin(estados)]
    if habitaciones:
        df_filtrado = df_filtrado[df_filtrado['bedrooms'].isin(habitaciones)]
    
    # Histograma de precios
    fig_hist = px.histogram(df_filtrado, x='price', nbins=50)
    
    # Dispersión Precio vs Tamaño
    fig_disp = px.scatter(df_filtrado, x='square_feet', y='price', color='bedrooms',
                          labels={'square_feet': 'Tamaño (ft²)', 'price': 'Precio'})
    
    # Mapa de Precios por Estado
    df_estado = df_filtrado.groupby('state')['price'].mean().reset_index()
    fig_mapa = px.choropleth(df_estado, locations='state', locationmode='USA-states',
                              color='price', color_continuous_scale='Viridis', scope='usa')
    
    # Estadísticas
    precio_promedio = f'${df_filtrado["price"].mean():,.2f}' if not df_filtrado.empty else 'N/A'
    precio_mediano = f'${df_filtrado["price"].median():,.2f}' if not df_filtrado.empty else 'N/A'
    desviacion_estandar = f'${df_filtrado["price"].std():,.2f}' if not df_filtrado.empty else 'N/A'
    
    return fig_hist, fig_disp, fig_mapa, precio_promedio, precio_mediano, desviacion_estandar

if __name__ == '__main__':
    app.run_server(debug=True)
