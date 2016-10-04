import threading
import time
import os

from flask import Blueprint, render_template, jsonify, current_app, request
from flask import url_for, Response, redirect, session

from . import login_manager
import flask
import flask_login

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
