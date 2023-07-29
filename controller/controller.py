# controller/controller.py
from flask import Blueprint, render_template_string
from service.services import setup_auth, get_spreadsheet_data, load_geojson, get_center, create_choropleth_map

main = Blueprint('main', __name__)


@main.route("/", methods=['GET'])
def home():
    gc = setup_auth()

    # Open the Google Sheet and get the data
    df = get_spreadsheet_data(gc,
                              'https://docs.google.com/spreadsheets/d/1kFyChQu7LjRG2ZXtptGVyj6uHUSNi9BnoEBaVFrB6oo/edit#gid=0')
    df[['latitude', 'longitude']] = df['Location'].str.split(',', expand=True).astype(float)

    gdf = load_geojson("res/Organisation_units.geojson")
    center_lat, center_lon = get_center(gdf)

    fig = create_choropleth_map(gdf, center_lat, center_lon)
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
