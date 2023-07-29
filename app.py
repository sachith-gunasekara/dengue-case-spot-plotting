from flask import Flask, render_template_string
from flask_ngrok import run_with_ngrok
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import geopandas as gpd

# Create a flask app
app = Flask(__name__)
run_with_ngrok(app)  # enables ngrok when the app is run


@app.route("/", methods=['GET'])
def home():
    # Set up the credentials for accessing the Google Sheet
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials/sa_credentials.json', scope)
    gc = gspread.authorize(credentials)

    # Open the Google Sheet and get the data
    worksheet = gc.open_by_url(
        'https://docs.google.com/spreadsheets/d/1kFyChQu7LjRG2ZXtptGVyj6uHUSNi9BnoEBaVFrB6oo/edit#gid=0').sheet1
    data = worksheet.get_all_values()
    headers = data.pop(0)

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(data, columns=headers)

    # Extract the location column and split it into latitude and longitude columns
    df[['latitude', 'longitude']] = df['Location'].str.split(',', expand=True).astype(float)

    # Load the GeoJSON file into a GeoDataFrame
    gdf = gpd.read_file("res/Organisation_units.geojson")

    # Calculate the center of the area covered by the GeoJSON file
    bounds = gdf.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    # Create an interactive choropleth map using Plotly
    fig = px.choropleth_mapbox(
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

    # Add the scatter plot of the location data to the map
    fig.add_scattermapbox(lat=df['latitude'], lon=df['longitude'], mode='markers')

    # Render the plot to HTML
    graphJSON = fig.to_html()

    # render template string
    return render_template_string("""
        <html>
            <body>
                {{graphJSON | safe}}
            </body>
        </html>
    """, graphJSON=graphJSON)


if __name__ == "__main__":
    app.run()
