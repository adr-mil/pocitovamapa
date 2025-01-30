#import time
import pandas as pd
import plotly.express as px
from plotly.express.colors import qualitative as color
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('page', __name__)
CSV_PATH = os.path.join(os.path.dirname(__file__), 'static/pocitova_mapa_2023.csv')
MARKERS = pd.read_csv(CSV_PATH)[['X', 'Y', 'Pocit', 'Pohlaví', 'Věk', 'Komentář']]
MARKERS['Věk'] = MARKERS['Věk'].fillna("neznámý")
MARKERS['Věk'] = MARKERS['Věk'].replace("nechci-odpovidat", "neznámý")
GRAPH_LIST = [
    ("genderGraph", "Počet záznamů podle pohlaví", "Pohlaví"),
    ("feelingGraph", "Počet záznamů podle pocitu", "Pocit"),
    ("ageGraph", "Počet záznamů podle věku", "Věk"),
]

@bp.route('/')
def page():
    return render_template("page.html")

def create_graphs(filters, bounds):
    filtered_markers = MARKERS
    for key in filters.keys():
        filtered_markers = filtered_markers[~filtered_markers[key].isin(filters[key])]

    in_bounds_markers = filtered_markers[
        (filtered_markers['X'] > bounds["_southWest"]["lng"]) &
        (filtered_markers['X'] < bounds["_northEast"]["lng"]) &
        (filtered_markers['Y'] > bounds["_southWest"]["lat"]) &
        (filtered_markers['Y'] < bounds["_northEast"]["lat"])
    ]

    colors = get_colors(filters)
    graph_dict = {}

    for graph_name, graph_title, variable in GRAPH_LIST:

        total_count = MARKERS[variable].value_counts().reset_index()
        total_count["type"] = "Celkový<br>počet"

        filter_count = filtered_markers[variable].value_counts().reset_index()
        filter_count["type"] = "Po filtrování"

        in_bounds_count = in_bounds_markers[variable].value_counts().reset_index()
        in_bounds_count["type"] = "Současný<br>úsek mapy"

        counts = pd.concat([total_count, filter_count, in_bounds_count])
        counts = counts.rename(columns={"count": "Počet"})
        print(counts)

        graph = px.bar(counts, x='type', 
                    y="Počet", 
                    title=graph_title,
                    color=variable,
                    color_discrete_map=colors,
                    barmode="group",
                    category_orders={
                        "Věk": [
                            "0-14", "15-24", "25-34", "35-44", 
                            "45-54", "55-64", "65+", "neznámý"
                        ]
                    })

        graph.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="left",
            x=0,
            ),
            legend_title=None,
            autosize=True,
        )

        graph_dict[graph_name] = graph.to_json()

    return (graph_dict, filtered_markers)

def get_colors(filters):
    colors = {
        "muž": 
            color.Set1[1] 
            if "muž" not in filters['Pohlaví'] 
            else color.Pastel1[1], 
        "žena": 
            color.Set1[0] 
            if "žena" not in filters['Pohlaví'] 
            else color.Pastel1[0], 
        "nechci odpovídat": 
            color.Set1[2] 
            if "nechci odpovídat" not in filters['Pohlaví'] 
            else color.Pastel1[2],
        "Místo, kde se cítím dobře":
            "green" 
            if "Místo, kde se cítím dobře" not in filters['Pocit'] 
            else "lightgreen",
        "Místo, které doporučím návštěvníkům":
            "yellow"
            if "Místo, které doporučím návštěvníkům" 
                not in filters['Pocit'] 
            else color.Pastel1[5],
        "Místo, kde se necítím dobře":
            color.Set1[0]
            if "Místo, kde se necítím dobře" 
                not in filters['Pocit'] 
            else color.Pastel1[0],
        "Místo, které by se mělo rozvíjet":
            "orange"
            if "Místo, které by se mělo rozvíjet"
                not in filters['Pocit'] 
            else color.Pastel1[4],
    }

    ageList = [
        "0-14", "15-24", "25-34", "35-44", 
        "45-54", "55-64", "65+", "neznámý"
    ]

    for i, age in enumerate(ageList):
        colors[age] = \
            color.Dark2[i] \
            if age not in filters['Věk'] \
            else color.Pastel2[i]

    return colors

@bp.route('/get-markers', methods=['POST'])
def get_markers():
    filters = request.json["filters"]
    bounds = request.json["bounds"]

    output_dict, filtered_markers = create_graphs(filters, bounds)
    output_dict["markers"] = filtered_markers.to_json(orient="split")

    return output_dict

@bp.route('/get-graphs', methods=['POST'])
def get_graphs():
    filters = request.json["filters"]
    bounds = request.json["bounds"]

    output_dict, _ = create_graphs(filters, bounds)

    return output_dict
