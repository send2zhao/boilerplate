import os
from flask import request, render_template
from flask_paginate import Pagination, get_page_args
from werkzeug import secure_filename

from . import api

from .. import db
from ..models import DbResource

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime


UPLOAD_FOLDER = os.path.dirname(__file__)
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
#File extension checking
def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


@api.route('/upload', methods=['GET','POST'])
def upload():
    message = ''
    page  = request.args.get('page', type=int, default=1)

    if request.method == 'POST':
        submitted_file = request.files['file']
        if submitted_file and allowed_filename(submitted_file.filename):
            filename = secure_filename(submitted_file.filename)
            submitted_file.save(os.path.join(UPLOAD_FOLDER, "..", "upload", filename))
            message = "Load '" + filename + "' completed."

    #tmp = DbResource.query.all()
    #print(tmp)
    pages = [1,2,3,4] #
    count = len(pages)
    pagination = Pagination(page=page, total=count, search=False,
                            record_name='pages', per_page = 30,
                            css_framework = 'bootstrap3')
    return render_template('upload.html',
                            message = message,
                            pagination = pagination,
                            pages = pages,
                            )
