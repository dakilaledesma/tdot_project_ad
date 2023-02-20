# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.processing import blueprint
import flask
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from flask_login import login_required
from pdf2image import convert_from_path
from glob import glob
import PyPDF2
import random
from PIL import Image, ImageFilter

from jinja2 import TemplateNotFound
import os
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "input_data"


# @blueprint.route("/upload")
# @login_required
# def upload():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and file.filename[:-4].lower() == ".pdf":
#             filename = file.filename
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('download_file', name=filename))
#     return '''
#         <!doctype html>
#         <title>Upload new File</title>
#         <h1>Upload new File</h1>
#         <form method=post enctype=multipart/form-data>
#           <input type=file name=file>
#           <input type=submit value=Upload>
#         </form>
#         '''

# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None


@blueprint.route('/<static>', methods=['GET'])
@login_required
def route_images(image_fn):
    try:
        send_from_directory("static", f"output_images/{image_fn}")
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except:
        return render_template('home/page-500.html'), 500


@blueprint.route('/upload', methods=["GET", 'POST'])
@login_required
def upload():
    # file = request.files.get('file')
    files = request.files.getlist('file')
    shutil.rmtree("./apps/processing/input_data/")
    os.makedirs("./apps/processing/input_data/")
    for file in files:
        file.save(f"./apps/processing/input_data/{file.filename}")
    saved_pdfs = glob(f"./apps/processing/input_data/*.pdf")
    images = convert_from_path(saved_pdfs[0], poppler_path=r"poppler\Library\bin")
    shutil.rmtree("./apps/static/output_images/")
    os.makedirs("./apps/static/output_images/")
    for i in range(len(images)):
        images[i].save(f"./apps/static/output_images/page{i}.jpg", "JPEG")

    if True:
        for fn in glob("./apps/static/output_images/*.jpg"):
            im = Image.open(fn)
            im = im.filter(ImageFilter.BoxBlur(20))
            im.save(fn)

    ret_string = """
<div class="card">
    <div class="card-header">
        <h4 class="card-title">Charts preview</h4>
    </div>
    <div class="card-body">
        <p class="demo">
            <table>
                <tr>
                    <td style="width: 0%;"><button class="btn btn-default" id="page_prev_prev">&#8592;</button></td>
                    <td align="center" style="width: 50%;">
                        <div id="preview_par">
                            <img src="static/output_images/page0.jpg" style="height: 75vh;">
                        </div>
                    </td>
                    <td style="width: 0%;"><button class="btn btn-default" id="page_next_prev">&#8594;</button></td>
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
<script>
    var page = 0;
    var max_pages = """ + str(len(images) - 1) + """;
    $('#process_pdf_button').click(function () {
        $.ajax({
            type: 'POST',
            url:  '/process',
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
            $("#main_panel").append(data.processed_string)
        },
        });
    });
    $('#page_next_prev').click(function () {
        if (page < max_pages){
            page = page + 1;
        }
         $('#preview_par').html(`<img src="static/output_images/page`+ page +`.jpg" style="height: 75vh;">`)
    });
    $('#page_prev_prev').click(function () {
        if (page > 0){
            page = page - 1;
        }
        
         $('#preview_par').html(`<img src="static/output_images/page`+ page +`.jpg" style="height: 75vh;">`)
    });
    
</script>
    """
    return flask.jsonify({"upload_string": ret_string})


@blueprint.route('/process', methods=["GET", 'POST'])
@login_required
def process():
    ret_string = """
<div class="card">
    <div class="card-header">
        <h4 class="card-title">Pre-processed charts</h4>
    </div>
    <div class="card-body">
        <p>
            <table id="basic-datatables" class="display table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Chart Name</th>
                            <th>Number of Pages</th>
                            <th>Signed</th>
                            <th>Predicted Value</th>
                            <th>Signature Preview</th>
                        </tr>
                    </thead>
                <tbody>
    """
    file_list = glob('./apps/processing/input_data/*.pdf')
    values = [random.randrange(0, 12500, 500) for _ in range(len(file_list) - 2)] + [0, 0]
    values.sort(reverse=True)
    for fn, value in zip(file_list, values):
        bn = os.path.basename(fn)
        file = open(fn, 'rb')
        pdf = PyPDF2.PdfReader(file)
        ret_string += f"""
                    <tr>
                        <td>{bn}</td>
                        <td>{len(pdf.pages)}</td>
                        <td>Yes</td>
                        <td>{value}</td>
                        <td>
                            <a href="static/predictions/prediction.png" target="_blank">
                                <button class="btn btn-info">
                                    <span class="btn-label">
                                        <i class="fa fa-info"></i>
                                    </span>
                                </button>
                            </a>
                        </td>
                    </tr>
        """

    ret_string += """
                </tbody>
            </table>
        </p>
        <p class="demo">
            <button class="btn btn-success" id="continue_charting_button">
                <span class="btn-label">
                    <i class="fa fa-check"></i>
                </span>
                Continue charting
            </button>
        </p>
    </div>
</div>
        """
    return flask.jsonify({"processed_string": ret_string})