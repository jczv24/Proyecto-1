import dash
from dash import dcc, html, State
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px 
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer
from functools import partial
from joblib import dump, load

# Función para filtrar datos
def FiltrarDatos(df, data_filtered):
    if df.shape[0] > 1:
        return pd.get_dummies(df, drop_first=True)
    
    elif df.shape[0] == 1:
        # Concatenar con data_filtered para garantizar la presencia de todas las categorías
        todos = pd.concat([df, data_filtered], ignore_index=True)
        
        todos = pd.get_dummies(todos, drop_first=True)
        
        # Asegurar que el orden de las columnas sea el mismo que en data_filtered
        todos = todos.reindex(columns=pd.get_dummies(data_filtered, drop_first=True).columns, fill_value=0)
        
        # Retornar solo la primera fila con las columnas en el orden correcto
        return todos.iloc[[0]]
    
#Cargar datos
df = pd.read_csv('datos_limpios.csv')
categorias_unicas = sorted(df['category'].unique())
estados_unicos = sorted(df['state'].unique())
mascotas_unicas = sorted(df['pets_allowed'].unique())
fuente_unicas = sorted(df['source'].unique())
has_photo_unicas = sorted(df['has_photo'].unique())

# Cargar modelo
data_filtro = df.drop(columns=['price'])
FiltrarDatosTransform = FunctionTransformer(partial(FiltrarDatos, data_filtered=data_filtro))

modelo = load("Ciencia_de_datos_Despliegue/RandomForestCompleto.joblib")


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

formulario_prediccion = dbc.Card(
    dbc.CardBody([
        html.H3("Formulario de Predicción", className="card-title", style={'textAlign': 'center', 'margin-bottom': '20px'}),

        dbc.Row([
            dbc.Col([
                dbc.Label("Número de baños", className="fw-bold"),
                dbc.Input(id='input-bathrooms', type='number', value=1, min=0, placeholder="Ejemplo: 2"),
            ], width=6),

            dbc.Col([
                dbc.Label("Número de habitaciones", className="fw-bold"),
                dbc.Input(id='input-bedrooms', type='number', value=1, min=0, placeholder="Ejemplo: 3"),
            ], width=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Metros cuadrados", className="fw-bold"),
                dbc.Input(id='input-square_feet', type='number', value=50, min=10, placeholder="Ejemplo: 100"),
            ], width=6),

            dbc.Col([
                dbc.Label("Estado", className="fw-bold"),
                dcc.Dropdown(
                    id='input-state',
                    options=[{'label': estado, 'value': estado} for estado in estados_unicos],
                    value=estados_unicos[0],
                    placeholder="Selecciona un estado"
                ),
            ], width=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Ciudad", className="fw-bold"),
                dcc.Dropdown(id='input-cityname', options=[], value=None, placeholder="Selecciona una ciudad"),
            ], width=6),

            dbc.Col([
                dbc.Label("Permite mascotas", className="fw-bold"),
                dcc.Dropdown(
                    id='input-pets_allowed',
                    options=[{'label': mascota, 'value': mascota} for mascota in mascotas_unicas],
                    value=mascotas_unicas[0],
                    placeholder="Selecciona una opción para las mascotas"
                    ),
            ], width=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Fuente", className="fw-bold"),
                dcc.Dropdown(
                    id='input-source',
                    options=[{'label': fuente, 'value': fuente} for fuente in fuente_unicas],
                    value=fuente_unicas[0],
                    placeholder="Selecciona una fuente"
                    ),
            ], width=6),

            dbc.Col([
                dbc.Label("Anuncio con foto?", className="fw-bold"),
                dcc.Dropdown(
                    id='input-photo',
                    options=[{'label': photo, 'value': photo} for photo in has_photo_unicas],
                    value=has_photo_unicas[0],
                    placeholder="Selecciona una opción"
                    )
            ], width=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Latitud", className="fw-bold"),
                dbc.Input(id='input-latitude', type='number', value=29.7714, placeholder="Ejemplo: 40.7128"),
            ], width=6),

            dbc.Col([
                dbc.Label("Longitud", className="fw-bold"),
                dbc.Input(id='input-longitude', type='number', value=-95.4343, placeholder="Ejemplo: -74.0060"),
            ], width=6)
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label('Categoría del anuncio', className="fw-bold"),
                dcc.Dropdown(
                    id='input-category',
                    options=[{'label': categoria, 'value': categoria} for categoria in categorias_unicas],
                    value=categorias_unicas[0],
                    placeholder='Selecciona una categoría'
                )
            ], width=6),
            
            dbc.Col([
                dbc.Label('Descripción del anuncio', className="fw-bold"),
                dbc.Textarea(id='input-description', placeholder='Descripción del anuncio', style={'height': '100px', 'width': '100%'}),
            ], width=6)
        ], className="mb-3"),

        html.Div(
            dbc.Button("Predecir Precio", id='predict-button', n_clicks = 1, color='primary', className="mt-3 w-100"),
            style={'textAlign': 'center'}
        )
        
    ]),
    className="shadow p-4 rounded-3",
    style={"backgroundColor": "#f8f9fa"}
)



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
        
    dbc.Container([
        formulario_prediccion
    ], fluid=True)
        
    ], style={'display': 'grid', 'grid-template-columns': '1fr', 'gap': '10px'}),

    # Salida de la predicción
    html.Div(id='output-prediction', style={
    'font-size': '32px',
    'font-weight': 'bold',
    'text-align': 'center',
    'margin-top': '50px',
    'color': '#084D6E'
})
            
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
                          color_continuous_scale='Viridis_r', labels={'square_feet': 'Tamaño (ft²)', 'price': 'Precio'})
    
    # Mapa de Precios por Estado
    df_estado = df_filtrado.groupby('state')['price'].mean().reset_index()
    fig_mapa = px.choropleth(df_estado, locations='state', locationmode='USA-states',
                              color='price', color_continuous_scale='Viridis_r', scope='usa')
    
    fig_mapa.update_layout(height = 700, margin={"r":0,"t":0,"l":0,"b":0})
    
    # Estadísticas
    precio_promedio = f'${df_filtrado["price"].mean():,.2f}' if not df_filtrado.empty else 'N/A'
    precio_mediano = f'${df_filtrado["price"].median():,.2f}' if not df_filtrado.empty else 'N/A'
    desviacion_estandar = f'${df_filtrado["price"].std():,.2f}' if not df_filtrado.empty else 'N/A'
    
    return fig_hist, fig_disp, fig_mapa, precio_promedio, precio_mediano, desviacion_estandar

# Callback para la predicción
@app.callback(
    Output('output-prediction', 'children'),
    Input('predict-button', 'n_clicks'),
    State('input-category', 'value'),
    State('input-bathrooms', 'value'),
    State('input-bedrooms', 'value'),
    State('input-photo', 'value'),
    State('input-square_feet', 'value'),
    State('input-cityname', 'value'),
    State('input-state', 'value'),
    State('input-pets_allowed', 'value'),
    State('input-source', 'value'),
    State('input-latitude', 'value'),
    State('input-longitude', 'value'),
    State('input-description', 'value')
)
def predict_price(n_clicks, category, bathrooms, bedrooms, photo, square_feet, cityname, state, pets_allowed, source, latitude, longitude, Description):
    if n_clicks > 0:
        # Crear un DataFrame con los datos del usuario
        data = pd.DataFrame([{
            "category": category,
            "bathrooms": bathrooms,
            "bedrooms": bedrooms,
            "has_photo": photo,
            "pets_allowed": pets_allowed,
            "square_feet": square_feet,
            "cityname": cityname,
            "state": state,
            "latitude": latitude,
            "longitude": longitude,
            "source": source,
            "Conteo body": len(str(Description))
        }])

        # Aplicar la misma transformación que usó el modelo
        try:
            prediction = modelo.predict(data)[0]
            return f"El precio estimado del arriendo mensual es: ${prediction:,.2f}"
        except Exception as e:
            return f"Error al predecir: {str(e)}"




if __name__ == '__main__':
    app.run_server(debug=True)
