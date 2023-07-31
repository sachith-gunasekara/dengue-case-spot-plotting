import gspread
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials


def setup_auth():
    # credentials_json = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
    credentials_json = "credentials/sa_credentials.json"
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, scope)
    gc = gspread.authorize(credentials)
    return gc


def get_spreadsheet_data(gc, url):
    worksheet = gc.open_by_url(url).sheet1
    data = worksheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    return df


def load_geojson(file_path):
    return gpd.read_file(file_path)


def get_center(gdf):
    bounds = gdf.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2
    return center_lat, center_lon


def create_choropleth_map(gdf, center_lat, center_lon):
    return px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        mapbox_style="carto-positron",
        zoom=9,
        center={
            "lat": center_lat,
            "lon": center_lon
        },
        opacity=0.5
    )


def create_scatter_map(df, fig):
    colors = [
        '#800080',  # Dark Purple
        '#0000A0',  # Dark Blue
        '#000000',  # Black
        '#FFA500',  # Orange
        '#FFFF00',  # Yellow
        '#FF0000',  # Red
        '#A52A2A',  # Brown
        '#008000',  # Green
        '#800000',  # Maroon
        '#808000'  # Olive
    ]

    for i, week_no in enumerate(df['Week No'].unique()):
        df_week = df[df['Week No'] == week_no]
        custom_data = list(zip(df_week['Patient Name'], df_week['MOH Area'], df_week['PHI Area']))
        fig.add_scattermapbox(
            lat=df_week['latitude'],
            lon=df_week['longitude'],
            mode='markers',
            name=f"Week {week_no}",  # This will represent the week number in the legend
            customdata=custom_data,  # adding extra data
            marker=go.scattermapbox.Marker(
                size=10,  # Adjust this to desired marker size
                color=colors[i % len(colors)],  # Assign a color to the marker
            ),
            hovertemplate=
            "%{customdata[0]}<br>" +
            "<b>MOH Area</b>: %{customdata[1]}<br>" +
            "<b>PHI Area</b>: %{customdata[2]}",
        )

    return fig
