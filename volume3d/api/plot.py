import os
from flask import request, render_template, url_for

from . import api


@api.route('/plot', methods=['GET'])
def plot():
    message = ''
    print(url_for('api.plot'))
    return render_template('plot.html',
                            message = message)
