from . import celery

from numpy import random
import time,timeit, sys, os, uuid

from flask_socketio import SocketIO
rabbitMq = SocketIO(message_queue='amqp://', async_mode = 'threading')

from Resource import Resource
DB_FOLDER = "db"
@celery.task
def generatePlot(message):
    print('generatePlot()')
    print('message: ', message)
    dbid = message['dbid']
    dbname   = Resource.dbName(dbid)
    dbname   = os.path.join(DB_FOLDER, dbname)
    print(dbid, dbname)
    resource = Resource.fromDb(dbname)

    # load the resource file
    uid = uuid.uuid1().get_hex()
    print('generatePlot...')
    (js, div) = resource.generatePlot()
    print('javascript:', js[:30])
    print('div:', div[:30])
    jsURL = os.path.join( "volume3d", "static", uid + ".js" )
    with open(jsURL, 'w') as f:
        f.write(js)
    jsURL = '/static/' + uid + '.js'
    print(jsURL)
    print('emit "plot available" event.')
    # to provent that the generating plot is faster than page loading!
    time.sleep(0.5)
    rabbitMq.emit("plot available", {'jsURL': jsURL, 'div': div},
                  room=message['sid'],
                  namespace = "/test")
