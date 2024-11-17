import pandas as pd
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('page', __name__)
CSV_PATH = os.path.join(os.path.dirname(__file__), 'static/pocitova_mapa_2023.csv')

@bp.route('/')
def page():
    return render_template("page.html")

@bp.route('/get-markers', methods=['POST'])
def get_markers():
    markers = pd.read_csv(CSV_PATH)
    markers = markers[['X', 'Y', 'Pocit']]

    print(markers)

    return markers.to_json()
