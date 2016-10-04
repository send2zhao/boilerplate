import threading
import time
import os
import uuid

from flask import Blueprint, render_template, jsonify, current_app, request
from flask import url_for, Response, redirect, session

from . import login_manager
import flask
import flask_login

from flask_paginate import Pagination, get_page_args

import cload
from models import DbFilter
from . import db
from utils import get_datatoken

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
from sqlalchemy import func

@main.route('/pages', methods=['GET','POST'])
@main.route('/pages/<id>', methods=['GET','POST'])
def pages(id=None):
    print('id:  ({0})'.format(id))
    fdata = flask.session.get('filter', None)
    qid   = flask.session.get('qid', "")
    page  = request.args.get('page', type=int, default=1)
    print('fdata: {0}'.format(fdata))
    if (request.method=="POST"):
        fdata = request.form['filter_data']
        if fdata.strip() == '': fdata = None
        flask.session['filter'] = fdata
        if (fdata is not None):
            qid = get_datatoken('{0}-{1}'.format(id,fdata))
            dbFilter = DbFilter(qid, id, fdata)
            if ( DbFilter.query.filter(DbFilter.qid == qid).first() is None):
                db.session.add(dbFilter)
                db.session.commit()
            flask.session['qid'] = qid
        return redirect(url_for('volume3d.pages', id = id))

    # sqlite file based
    if id is not None:
        dbfile = '{0}.sqlite'.format(id)
        if not os.path.exists(dbfile):
            t_db = cload.DB
        else:
            t_db = "sqlite:///{0}.sqlite".format(id)
    else:
        t_db = cload.DB

    count = 0
    if (fdata is not None):
        try:
            count, imageViewLogs = cload.filterRaw(fdata, [(page-1)*30, (page*30)], db=t_db)
        except:
            print('syntaxError')
            imageViewLogs = []; flask.session['filter'] = None
    else:
        engine = create_engine(t_db)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session   = DBSession()
        count = session.query(ImageViewLog).filter(ImageViewLog.time > datetime(2016,9,1)).count()
        imageViewLogs = session.query(ImageViewLog).filter(ImageViewLog.time > datetime(2016,9,1))[(page-1)*30:(page*30)]
        session.close()
    # pagination is an object to track the pages as well the views of the page icons.
    pagination = Pagination(page=page, total=count, search=False, record_name='pages', per_page = 30, css_framework = 'bootstrap3')
    return render_template('pages.html',
                           id = id,
                           pages=imageViewLogs,
                           pagination=pagination,
                           filter=fdata,
                           qid = qid,
                           )
