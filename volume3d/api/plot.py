import os, uuid
from flask import request, redirect, render_template, url_for

from . import api
from .. import task3

@api.route('/plot', methods=['GET'])
def plot():
    message = {}
    print(url_for('api.plot'))
    return render_template('plot.html',
                            message = message)

@api.route('/plot/<id>', methods=['GET'])
def plotId(id=None):
    """
    I want to send this page right away
    then, set room id to both the page as well as
    the backend.
    In the backend, if it is done, then it will emit
    the result to the front page automatically.

    [WARNING] There is a racing condition.
    PROBLEM: what if plot generating is fast than the
    page?  Page will not be recieving the event of `plot Ready`
    since it is already happened.
    """

    if (id is None):
        print("redirect to page")
        redirect(url_for('plot'))
    # check the id  exists


    # let start to generate the plot
    sid = str(uuid.uuid1())
    message = {'sid': sid, 'dbid': id}

    print('Processing plot request. %s' %message['dbid'])
    task3.generatePlot.delay(message)

    # rendering
    message['ioroomid']=sid
    return render_template('plot.html',
                            message=message)
