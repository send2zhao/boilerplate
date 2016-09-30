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
    name = message['name']
    name = os.path.join('upload', name)
    start_time = timeit.default_timer()
    with open(name, 'wb') as f:
        f.write(message["data"])
    print('save xrslog: ', timeit.default_timer() - start_time)
    rabbitMq.emit('my response', {'data': 'Saved'}, room=sid, namespace='/test')

    if (name.endswith(".xrslog")):
        start_time = timeit.default_timer()
        cload.loadLogToDb(name, db="sqlite:///{0}.sqlite".format(sid), new = True)
        print('loadLogToDb: ', timeit.default_timer() - start_time)
        rabbitMq.emit('my response', {'data': 'loaded to DB'}, room=sid, namespace='/test')
