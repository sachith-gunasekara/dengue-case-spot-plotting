import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from helper import \
    get_spreadsheet_data, \
    load_geojson, \
    get_center, \
    create_choropleth_map, \
    setup_auth, \
    create_scatter_map

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = 'Matale Dengue Case Spotting'

app.layout = dbc.Container([  # fluid Bootstrap Container
    dbc.Row([  # Row for the header
        dbc.Col(
            html.H1('Matale Dengue Case Spotting', style={'textAlign': 'center'}),
            width=12
        )
    ]),
    dbc.Row([  # Row for the dropdowns
        dbc.Col(  # Column for the first dropdown
            dcc.Dropdown(
                id='moh-dropdown',
                placeholder="Select a MOH Area",
                multi=True
            ),
            width={'size': 6, 'offset': 0, 'order': 1},
            xs={'size': 12, 'offset': 0, 'order': 'first'}
        ),
        dbc.Col(  # Column for the second dropdown
            dcc.Dropdown(
                id='phi-dropdown',
                placeholder="Select a PHI Area",
                multi=True
            ),
            width={'size': 6, 'offset': 0, 'order': 2},
            xs={'size': 12, 'offset': 0, 'order': 'last'}
        ),
    ]),
    dbc.Row([  # Row for the map
        dbc.Col(
            dcc.Graph(
                id='map-graph'
            ),
            width=12
        )
    ]),
], fluid=True)

gc = setup_auth()
df = get_spreadsheet_data(gc,
                          'https://docs.google.com/spreadsheets/d/1kFyChQu7LjRG2ZXtptGVyj6uHUSNi9BnoEBaVFrB6oo/edit#gid=0')


@app.callback(
    Output('moh-dropdown', 'options'),
    Input('map-graph', 'figure')
)
def set_moh_options(figure):
    moh_areas = df['MOH Area'].unique()
    return [{'label': i, 'value': i} for i in moh_areas]


@app.callback(
    Output('phi-dropdown', 'options'),
    Input('moh-dropdown', 'value')
)
def set_phi_options(selected_moh):
    if selected_moh is None:
        return []
    phi_areas = df[df['MOH Area'].isin(selected_moh)]['PHI Area'].unique()
    return [{'label': i, 'value': i} for i in phi_areas]


@app.callback(
    Output('map-graph', 'figure'),
    Input('moh-dropdown', 'value'),
    Input('phi-dropdown', 'value')
)
def update_map(selected_moh, selected_phi):
    df[['latitude', 'longitude']] = df['Location'].str.split(',', expand=True).astype(float)

    gdf = load_geojson("res/Organisation_units.geojson")
    center_lat, center_lon = get_center(gdf)

    figure = create_choropleth_map(gdf, center_lat, center_lon)

    if not selected_moh and not selected_phi:
        figure = create_scatter_map(df, figure)
    else:
        # If a MOH area is selected but no PHI area is selected, filter by MOH area
        if selected_phi is None:
            filtered_df = df[df['MOH Area'].isin(selected_moh)]
        # If a PHI area is selected but no MOH area is selected, filter by PHI area
        elif selected_moh is None:
            filtered_df = df[df['PHI Area'].isin(selected_phi)]
        # If both a MOH and PHI area are selected, filter by both
        else:
            filtered_df = df[(df['MOH Area'].isin(selected_moh)) & (df['PHI Area'].isin(selected_phi))]
        figure = create_scatter_map(filtered_df, figure)

    figure.update_layout(
        autosize=True,
        margin=dict(l=10, r=0, b=0, t=20),
        geo=dict(
            showland=True,
            landcolor="rgb(20, 20, 20)",
            countrycolor="rgb(20, 20, 20)",
            lakecolor="rgb(255, 255, 255)",
            showocean=True,
            oceancolor="rgb(30, 30, 30)",
            showlakes=True
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
    )

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
