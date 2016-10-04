import os
from flask import request, render_template
from werkzeug import secure_filename

from . import api

UPLOAD_FOLDER = os.path.dirname(__file__)
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
#File extension checking
def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


@api.route('/upload', methods=['GET','POST'])
def upload():
    message = ''
    if request.method == 'POST':
        submitted_file = request.files['file']
        if submitted_file and allowed_filename(submitted_file.filename):
            filename = secure_filename(submitted_file.filename)
            submitted_file.save(os.path.join(UPLOAD_FOLDER, "..", "upload", filename))
            message = "Load '" + filename + "' completed."
    return render_template('upload.html',
                            message = message)
