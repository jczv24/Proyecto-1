import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Cargar datos (ajusta la ruta según tu archivo)
df = pd.read_csv('datos_apartamentos_rent.csv', encoding_errors = 'replace', delimiter = ';')

# Inicializar la app Dash con el estilo LUX
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

# Layout del tablero
app.layout = html.Div([ 
    html.H1('Arrendamiento de Apartamentos', style={'textAlign': 'center'})
,

    # Filtros (Estado y Número de habitaciones uno al lado de otro)
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

    # Estadísticas Resumidas en tarjetas (arriba)
    html.Div([
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Precio Promedio", className="card-title", style={'textAlign': 'center'}),
                        html.P(id='precio-promedio', className="card-text", style={'textAlign': 'center'})
                    ]),
                    color="dark", inverse=True
                ), width=4
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Precio (Mediana)", className="card-title", style={'textAlign': 'center'}),
                        html.P(id='precio-mediano', className="card-text", style={'textAlign': 'center'})
                    ]),
                    color="dark", inverse=True
                ), width=4
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([ 
                        html.H4("Desviación Estándar", className="card-title", style={'textAlign': 'center'}),
                        html.P(id='desviacion-estandar', className="card-text", style={'textAlign': 'center'})
                    ]),
                    color="dark", inverse=True
                ), width=4
)
        ])
    ], style={'padding': '20px'}),


    # Visualizaciones

    html.Div([
        # Fila para las dos primeras gráficas al lado (Distribución de Precios y Precio vs Tamaño)
        dbc.Row([
            # Tarjeta para el histograma de precios
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.H4('Distribución de Precios', style={'textAlign': 'center'}),
                            dcc.Graph(id='histograma-precios')  # El gráfico
                        ], style={'marginBottom': '15px'}),

                        # Descripción debajo del gráfico
                        html.Div([
                            html.P('Distribución de precios de los apartamentos en los estados seleccionados.')
                        ], style={'textAlign': 'center', 'color': 'gray'})
                    ]),
                    style={'marginBottom': '20px'}
                ),
                width=6  # Establecemos el ancho para que ocupe la mitad de la fila
            ),

            # Tarjeta para el gráfico de dispersión
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.H4('Precio vs Tamaño (ft²)', style={'textAlign': 'center'}),
                            dcc.Graph(id='dispersion-precio-tamano')  # El gráfico
                        ], style={'marginBottom': '15px'}),

                        # Descripción debajo del gráfico
                        html.Div([
                            html.P('Relación entre el precio de los apartamentos y su tamaño en pies cuadrados.')
                        ], style={'textAlign': 'center', 'color': 'gray'})
                    ]),
                    style={'marginBottom': '20px'}
                ),
                width=6  # Establecemos el ancho para que ocupe la mitad de la fila
            )
        ], style={'marginBottom': '20px'}),  # Separa la fila de las gráficas

        # Tarjeta para el mapa de precios
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H4('Precio Promedio por Estado', style={'textAlign': 'center'}),
                    dcc.Graph(id='mapa-precios')  # El gráfico
                ], style={'marginBottom': '15px'}),

                # Descripción debajo del gráfico
                html.Div([
                    html.P('Precio promedio de los apartamentos en cada estado.')
                ], style={'textAlign': 'center', 'color': 'gray'})
            ]),
            style={'marginBottom': '20px'}
        )
    ], style={'width': '80%', 'margin': 'auto'})

])

# Callbacks para actualizar gráficos y estadísticas
@app.callback(
    [Output('histograma-precios', 'figure'),
     Output('dispersion-precio-tamano', 'figure'),
     Output('mapa-precios', 'figure'),
     Output('precio-promedio', 'children'),
     Output('precio-mediano', 'children'),
     Output('desviacion-estandar', 'children')],  # Agregado Output para la desviación estándar
    [Input('ciudad-filtro', 'value'),
     Input('habitaciones-filtro', 'value')]
)
def actualizar_graficos(estados, habitaciones):
    # Filtrar datos
    df_filtrado = df.copy()
    if estados:
        df_filtrado = df_filtrado[df_filtrado['state'].isin(estados)]
    if habitaciones:
        df_filtrado = df_filtrado[df_filtrado['bedrooms'].isin(habitaciones)]
    
    # Histograma de precios
    fig_hist = px.histogram(df_filtrado, x='price', nbins=50)
    
    # Gráfico de dispersión (Precio vs Tamaño)
    fig_disp = px.scatter(df_filtrado, x='square_feet', y='price', color='bedrooms',
                          labels={'square_feet': 'Tamaño (ft²)', 'price': 'Precio'})
    
    # Mapa de Precios por Estado
    promedio_estado = df_filtrado.groupby('state')['price'].mean().reset_index()
    fig_mapa = px.choropleth(
        promedio_estado,
        locations='state',         # Nombre de los estados
        locationmode='USA-states', # Modo para estados de EE.UU.
        color='price',             # Variable a colorear
        hover_name='state',        # Información al pasar el cursor
        color_continuous_scale='Blues',
        scope='usa',               # Limita el mapa a EE.UU.
        labels={'price': 'Precio Promedio'}
    )
    fig_mapa.update_layout()
    
    # Estadísticas Resumidas
    precio_promedio = df_filtrado['price'].mean()
    precio_mediana = df_filtrado['price'].median()
    desviacion_estandar = df_filtrado['price'].std()  # Desviación estándar
    
    return fig_hist, fig_disp, fig_mapa, f"${precio_promedio:,.2f}", f"${precio_mediana:,.2f}", f"${desviacion_estandar:,.2f}"  # Incluye la desviación estándar

# Ejecutar la app
if __name__ == '__main__':
    app.run_server(debug=True)
