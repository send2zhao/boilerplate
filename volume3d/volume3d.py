import threading
import time
import os

from flask import Blueprint, render_template, jsonify, current_app, request
from flask import url_for, Response, redirect, session

from . import login_manager
import flask
import flask_login

from flask_paginate import Pagination, get_page_args
from werkzeug import secure_filename
import cload

# Our mock database.
users = {'Jenny': {'pw': 'Zhao'}}
class User(flask_login.UserMixin):
    pass
@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user
@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return
    user = User()
    user.id = email
    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']
    return user

main = Blueprint('volume3d', __name__)

def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'static',
            filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)

@main.route('/')
def index():
    """Serve client-side application."""
    return render_template('index.html')
    #return url_for('static', filename='index.html')
    #content = get_file('index.html')
    #return Response(content, mimetype="text/html")

@main.route('/socket')
def index2():
    """Serve client-side application."""
    return render_template('socket.html')
    #return url_for('static', filename='index.html')
    #content = get_file('index.html')
    #return Response(content, mimetype="text/html")

@main.route('/socket2')
def socket2():
    """Serve client-side application."""
    return render_template('socket2.html')
    #return url_for('static', filename='index.html')
    #content = get_file('index.html')
    #return Response(content, mimetype="text/html")

@main.route('/socket3')
def socket3():
    """Serve client-side application."""
    return render_template('socket3.html')
    #return url_for('static', filename='index.html')
    #content = get_file('index.html')
    #return Response(content, mimetype="text/html")


@main.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({'requests_per_second': 'none'})
    #return jsonify({'requests_per_second': stats.requests_per_second()})


## login form
@main.route('/login', methods=['GET', 'POST'])
def login():
    import flask_login
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='pw' id='pw' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''

    email = flask.request.form['email']
    print(email)
    print('request',flask.request.form['pw'] )
    if flask.request.form['pw'] == users[email]['pw']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        #return flask.redirect(flask.url_for('/stats'))
        return jsonify({'check password': 'passed'})

    return 'Bad login'


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ImageViewLog import ImageViewLog, Base
from datetime import datetime

"""
Provide the view of the log.
"""
@main.route('/pages', methods=['GET','POST'])
@main.route('/pages/<id>', methods=['GET','POST'])
def pages(id=None):
    #print("sid:", request.sid)
    fdata = flask.session.get('filter', None)
    page = request.args.get('page', type=int, default=1)
    print('fdata: {0}'.format(fdata))
    if (request.method=="POST"):
        fdata = request.form['filter_data']
        if fdata.strip() == '': fdata = None
        flask.session['filter'] = fdata
        return redirect(url_for('volume3d.pages'))

    # sqlite file based
    if id is not None:
        dbfile = '{0}.sqlite'.format(id)
        if not os.path.exists(dbfile):
            t_db = cload.DB
        else:
            t_db = "sqlite:///{0}.sqlite".format(id)
    else:
        t_db = cload.DB
    engine = create_engine(t_db)
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    #imageViewLogs = session.query(ImageViewLog).filter(ImageViewLog.level.like("%"+"Error"+"%")).order_by(ImageViewLog.time).order_by(ImageViewLog.logger)
    count = 0
    if (fdata is not None):
        try:
            count, imageViewLogs = cload.filterRaw(fdata, [(page-1)*30, (page*30)])
        except:
            print('syntaxError')
            imageViewLogs = []; flask.session['filter'] = None
    else:
        count = session.query(ImageViewLog).filter(ImageViewLog.time > datetime(2016,9,1)).count()
        imageViewLogs = session.query(ImageViewLog).filter(ImageViewLog.time > datetime(2016,9,1))[(page-1)*30:(page*30)]
    session.close()
    # pagination is an object to track the pages as well the views of the page icons.
    pagination = Pagination(page=page, total=count, search=False, record_name='pages', per_page = 30, css_framework = 'bootstrap3')
    return render_template('pages.html',
                           pages=imageViewLogs,
                           pagination=pagination,
                           filter=fdata,
                           )

UPLOAD_FOLDER = os.path.dirname(__file__)
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
#File extension checking
def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@main.route('/upload', methods=['GET','POST'])
def upload():
    message = ''
    if request.method == 'POST':
        submitted_file = request.files['file']
        if submitted_file and allowed_filename(submitted_file.filename):
            filename = secure_filename(submitted_file.filename)
            submitted_file.save(os.path.join(UPLOAD_FOLDER, "..", "upload", filename))
            message = "Load '" + filename + "' completed."
            #return redirect(url_for('upload', message=message))

    return render_template('upload.html',
                            message = message)
