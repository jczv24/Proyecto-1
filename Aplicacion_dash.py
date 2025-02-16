import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Cargar datos (ajusta la ruta según tu archivo)
df = pd.read_csv('datos_apartamentos_rent.csv', encoding_errors = 'replace', delimiter = ';')

# Inicializar la app Dash
app = dash.Dash(__name__)

# Layout del tablero
app.layout = html.Div([
    html.H1('Tablero de Arrendamiento de Apartamentos'),
    
    # Filtros
    html.Div([
        html.Label('Estado:'),
        dcc.Dropdown(
            id='ciudad-filtro',
            options=[{'label': estado, 'value': estado} for estado in df['state'].dropna().unique()],
            value=None,
            placeholder='Selecciona un estado',
            multi=True
        ),
        html.Label('Número de habitaciones:'),
        dcc.Dropdown(
            id='habitaciones-filtro',
            options=[{'label': str(hab), 'value': hab} for hab in sorted(df['bedrooms'].dropna().unique())],
            value=None,
            placeholder='Selecciona número de habitaciones',
            multi=True
        )
    ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
    
    # Visualizaciones
    html.Div([
        dcc.Graph(id='histograma-precios'),
        dcc.Graph(id='dispersion-precio-tamano'),
        dcc.Graph(id='mapa-precios')
    ], style={'width': '65%', 'display': 'inline-block', 'padding': '10px'}),
    
    # Estadísticas Resumidas
    html.Div(id='estadisticas-resumen')
])

# Callbacks para actualizar gráficos y estadísticas
@app.callback(
    [Output('histograma-precios', 'figure'),
     Output('dispersion-precio-tamano', 'figure'),
     Output('mapa-precios', 'figure'),
     Output('estadisticas-resumen', 'children')],
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
    fig_hist = px.histogram(df_filtrado, x='price', nbins=50, title='Distribución de Precios')
    
    # Gráfico de dispersión (Precio vs Tamaño)
    fig_disp = px.scatter(df_filtrado, x='square_feet', y='price', color='bedrooms',
                          title='Precio vs Tamaño (ft²)', 
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
    fig_mapa.update_layout(title_text='Precio Promedio de Arrendamiento por Estado')
    
    # Estadísticas Resumidas
    precio_promedio = df_filtrado['price'].mean()
    precio_mediana = df_filtrado['price'].median()
    estadisticas = f"""
    Precio Promedio: ${precio_promedio:,.2f}  
    Precio Mediana: ${precio_mediana:,.2f}
    """
    
    return fig_hist, fig_disp, fig_mapa, estadisticas

# Ejecutar la app
if __name__ == '__main__':
    app.run_server(debug=True)
