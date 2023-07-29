# controller/controller.py
from flask import Blueprint
from service.services import return_moh_area_plot

main = Blueprint('main', __name__)


@main.route("/", methods=['GET'])
def home():
    return return_moh_area_plot()
