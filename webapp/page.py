#import time
import pandas as pd
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('page', __name__)
CSV_PATH = os.path.join(os.path.dirname(__file__), 'static/pocitova_mapa_2023.csv')
MARKERS = pd.read_csv(CSV_PATH)[['X', 'Y', 'Pocit', 'Pohlaví', 'Věk', 'Komentář']]

@bp.route('/')
def page():
    return render_template("page.html")

@bp.route('/get-markers', methods=['POST'])
def get_markers():
    #start = time.time()

    #print("time for json transform: ", time.time() - start)

    return MARKERS.to_json(orient="split")
