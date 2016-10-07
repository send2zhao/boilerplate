from . import celery

from numpy import random
import time,timeit, sys, os, uuid

from flask_socketio import SocketIO
rabbitMq = SocketIO(message_queue='amqp://')

from Resource import Resource

@celery.task
def generatePlot(message):
    pass
    # load the resource file
    uid = uuid.uuid1().get_hex()
    resource = Resource(r'2015.11.20.1119.CSV')
    (js, div) = resource.generatePlot()
    jsURL = os.path.join( "volume3d", "static", uid + ".js" )
    with open(jsURL, 'w') as f:
        f.write(js)
    jsURL = '/static/' + uid + '.js'
    print(jsURL)
    rabbitMq.emit("plot available", {'jsURL': jsURL, 'div': div}, namespace = "/test")
