from helper.helper import setup_auth
import pandas as pd
import geopandas as gpd
import plotly.express as px


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
        zoom=8,
        center={
            "lat": center_lat,
            "lon": center_lon
        },
        opacity=0.5
    )
