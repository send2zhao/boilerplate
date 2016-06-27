import threading
import time
import os

from flask import Blueprint, render_template, jsonify, current_app
from flask import url_for, Response
#from .models import User
#from .events import push_model
#from . import db, stats

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


@main.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({'requests_per_second': 'none'})
    #return jsonify({'requests_per_second': stats.requests_per_second()})
