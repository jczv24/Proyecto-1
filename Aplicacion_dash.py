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
    # Título
    dbc.Row(
        dbc.Col(html.H1('Arrendamiento de Apartamentos', className="text-center text-primary"), width=12),
        className="mb-4"
    ),
    
    # Filtros y estadisticas resumidas
    dbc.Row([
        dbc.Col([
            html.Label('Estado:', className="form-label"),
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
        ], width=4),
        
        dbc.Col(html.Div(id='estadisticas-resumen', className="alert alert-info", style = {'height': '100px', 'display': 'flex', 'align-items': 'center'}), width=4)
    ], className="mb-0"),

    # Visualizaciones
    dbc.Row([
        dbc.Col(dcc.Graph(id='histograma-precios'), width=6),
        dbc.Col(dcc.Graph(id='dispersion-precio-tamano'), width=6)
    ], className="mb-0"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='mapa-precios', style = {'height': '800px'}), width=12)
    ], className="mb-0")

    # Estadísticas Resumidas
    #dbc.Row([
        #dbc.Col(html.Div(id='estadisticas-resumen', className="alert alert-info"), width=12)
    #], className="mb-0")
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
