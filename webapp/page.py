#import time
import pandas as pd
import plotly.express as px
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
    filters = request.json["filters"]
    print("Filters: ", filters)

    bounds = request.json["bounds"]
    print("Bounds: ")
    print(bounds)

    filtered_markers = MARKERS
    for key in filters.keys():
        filtered_markers = filtered_markers[~filtered_markers[key].isin(filters[key])]

    in_bounds_markers = filtered_markers[
        (filtered_markers['X'] > bounds["_southWest"]["lng"]) &
        (filtered_markers['X'] < bounds["_northEast"]["lng"]) &
        (filtered_markers['Y'] > bounds["_southWest"]["lat"]) &
        (filtered_markers['Y'] < bounds["_northEast"]["lat"])
    ]

    #print(in_bounds_markers)

    #start = time.time()
    gender_total_count = MARKERS['Pohlaví'].value_counts().reset_index()
    gender_total_count["type"] = "Celkový<br>počet"

    gender_filter_count = filtered_markers['Pohlaví'].value_counts().reset_index()
    gender_filter_count["type"] = "Po filtrování"

    in_bounds_count = in_bounds_markers['Pohlaví'].value_counts().reset_index()
    in_bounds_count["type"] = "Současný<br>úsek mapy"

    gender_group_count = pd.concat([gender_total_count, gender_filter_count, in_bounds_count])
    gender_group_count = gender_group_count.rename(columns={"count": "Počet"})
    print(gender_group_count)

    colors = {
        "muž": px.colors.qualitative.Set1[1] 
                if "muž" not in filters['Pohlaví'] 
                else px.colors.qualitative.Pastel1[1], 
        "žena": px.colors.qualitative.Set1[0] 
                if "žena" not in filters['Pohlaví'] 
                else px.colors.qualitative.Pastel1[0], 
        "nechci odpovídat": px.colors.qualitative.Set1[2] 
                if "nechci odpovídat" not in filters['Pohlaví'] 
                else px.colors.qualitative.Pastel1[2]
    }

    genderGraph = px.bar(gender_group_count, x='type', 
                         y="Počet", 
                         title="Počet záznamů podle pohlaví",
                         color='Pohlaví',
                         color_discrete_map=colors,
                         barmode="group",
                         )

    genderGraph.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="left",
        x=0,
        ),
        legend_title=None,
        autosize=True,
    )

    #print("time for json transform: ", time.time() - start)

    return {
        "markers": filtered_markers.to_json(orient="split"),
        "genderGraph": genderGraph.to_json()
        }
