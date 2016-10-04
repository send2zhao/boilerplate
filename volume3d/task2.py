from . import celery
#from . import socketio
from numpy import random
import time,timeit, sys, os

import cload


from flask_socketio import SocketIO
rabbitMq = SocketIO(message_queue='amqp://')

@celery.task
def long_task2(word):
    print('long_task2(): %s' % word)
    rabbitMq.emit('my response', {'data': 'I am finished the long_task2()'},
             namespace='/test')

@celery.task
def long_task_loadDBfile(sid, message):
    print('long_task_loadDBfile()')
    rabbitMq.emit('my response', {'data': 'processing ...'}, namespace='/test')

    if ('numBlob' in message.keys()):
        sid = message['sid']
        print('sid: %s' %sid)
        folder = os.path.join('upload', sid)
        #if (not os.path.exists(folder)):
        #    os.makedirs(folder)
        name = os.path.join('upload', "{0}.{1}".format(message['sid'], message['blobId']))
        with open(name, 'wb') as f:
            f.write(message["data"])

    else:
        name = message['name']
        name = os.path.join('upload', name)
        addToExistDb = message['addToExistDb']

        start_time = timeit.default_timer()
        with open(name, 'wb') as f:
            f.write(message["data"])
        print('save {0}: '.format(name), timeit.default_timer() - start_time)
        rabbitMq.emit('my response', {'data': 'Saved'}, namespace='/test')

        if (name.endswith(".xrslog")):
            start_time = timeit.default_timer()
            cload.loadLogToDb(name, db="sqlite:///{0}.sqlite".format(sid), new = not addToExistDb)
            print('loadLogToDb: ', timeit.default_timer() - start_time)
            rabbitMq.emit('new data available', {'data': 'New data is available. <a href="{{ url_for("api.pages") }}"> ({0})'.format(sid)}, namespace='/test')
            rabbitMq.emit('my response', {'data': 'New data is available. <a href="{{ url_for("api.pages") }}"> ({0})'.format(sid)}, namespace='/test')
