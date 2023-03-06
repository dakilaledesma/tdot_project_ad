# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.processing import blueprint
import flask
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from flask_login import login_required
from jinja2 import TemplateNotFound
import googlemaps
import json
import pandas as pd
from collections import defaultdict
import os

print(os.getcwd())
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "input_data"

option_df = pd.read_excel("apps/processing/data/ResearchProjectSpreadsheet.xlsx", sheet_name="DesignConsiderations")
categories_df = option_df[["Unnamed: 0", "Subcategory"]][3:]

category_dict = defaultdict(dict)
curr_category = None
for index, row in categories_df.iterrows():
    category = row["Unnamed: 0"]
    subcategory = row["Subcategory"]
    if category != curr_category and str(category) != "nan":
        curr_category = category

    if str(subcategory) != "nan":
        category_dict[curr_category][subcategory] = index
    else:
        category_dict[curr_category][category] = index

print(category_dict)






# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None


@blueprint.route('/placesdata')
@login_required
def placesdata():
    with open("../static/assets/tokens/tokens") as tokens_file:
        tokens = json.load(tokens_file)

    opt_response = flask.request.args.get("options")
    opts_dict = {}
    opts_str = opt_response.split(",,")
    for option in opts_str:
        k, v = option.split(": ")
        opts_dict[k] = v

    gmaps = googlemaps.Client(key=tokens["gmaps"])

    nearby_result = gmaps.places_nearby(location=(opts_dict["lat"], opts_dict["lon"]),
                                        radius=500,
                                        keyword="park")

    places = '<br>'.join(nearby_result["results"])

    print(places, opts_dict["lat"], opts_dict["lon"])

    ret_string = f"""
<div class="card">
    <div class="card-header">
        <h4 class="card-title">Charts preview</h4>
    </div>
    <div class="card-body">
        <p class="demo">
            <table>
                <tr>
                    <td>
                        Latitude: {opts_dict["lat"]}
                    </td>
                    <td>
                        Longitude: {opts_dict["lon"]}
                    </td>
                </tr>
                <tr>
                    <td>
                        Places data: {places}
                    </td>
                    <td>
                        Longitude: {opts_dict["lon"]}
                    </td>
                </tr>
            </table>
        </p>
        <p>
        <button class="btn btn-success" id="process_pdf_button">
            <span class="btn-label">
                <i class="fa fa-check"></i>
            </span>
            Pre-process
        </button>
        </p>
    </div>
</div>    
    """
    return flask.jsonify({"places_string": ret_string})


@blueprint.route('/test')
@login_required
def test():
    ret_string = "test"
    print(ret_string)
    return flask.jsonify({"places_string": ret_string})

@blueprint.route('/sp_load_majors')
@login_required
def sp_load_majors():
    ret_string = """
<div class="card" id="load_majors_card">
    <div class="card-header">
        <h4 class="card-title">Spreadsheet Tool</h4>
    </div>
    <div class="card-body">
        <p class="demo">
            <h3>Major Categories</h3>
                <select id="major_categories">
                    <option value="none" selected disabled hidden>Select a major category</option>
    """
    for k in category_dict.keys():
        ret_string += f'<option value="{k}">{k}</option>'
    ret_string += """
                </select>
        </p>
    </div>
</div>
    """

    return flask.jsonify({"return_string": ret_string})

@blueprint.route('/sp_load_subcategories')
@login_required
def sp_load_subcategories():
    opt_response = flask.request.args.get("major_category")
    sub_dict = category_dict[opt_response]
    ret_string = """
<div class="card" id="load_subc_card">
    <div class="card-body">
        <p class="demo">
            <h3>Subcategories</h3>
                <select id="subcategories">
                    <option value="none" selected disabled hidden>Select a subcategory</option>
    """
    for k in sub_dict.keys():
        ret_string += f'<option value="{k}">{k}</option>'
    ret_string += """
                </select>
        </p>
    </div>
</div>
    """

    return flask.jsonify({"return_string": ret_string})

@blueprint.route('/sp_load_params')
@login_required
def sp_load_params():
    major_category = flask.request.args.get("major_category")
    subcategory = flask.request.args.get("subcategory")
    ret_string = """
<div class="card" id="load_params_card">
    <div class="card-header">
        <h4 class="card-title">Values</h4>
    </div>
    <div class="card-body">
        <p class="demo">
        
"""
    for col in option_df.columns[2:]:
        col_header = [v for v in option_df[col][:3] if str(v) != "nan"]
        headers = []
        for idx in range(3, -1, -1):
            h_val = idx + 2
            try:
                headers.append(f'<h{h_val}>{col_header[idx]}</h{h_val}>')
            except IndexError:
                pass
        headers.reverse()

        ret_string += "".join(headers)
        ret_string += f"""
            <p>{option_df[col][category_dict[major_category][subcategory]]}</p>
        """

    ret_string += f"""
            </p>
        </div>
    </div>
    """

    return flask.jsonify({"return_string": ret_string})

