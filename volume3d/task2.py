from . import celery
#from . import socketio
from numpy import random
import time,timeit, sys, os

import cload
from Resource import Resource


from flask_socketio import SocketIO
rabbitMq = SocketIO(message_queue='amqp://')

DB_FOLDER = "db"

@celery.task
def long_task2(word):
    print('long_task2(): %s' % word)
    rabbitMq.emit('my response', {'data': 'I am finished the long_task2()'},
             namespace='/test')

@celery.task
def task2_loadFile(sid, message):
    print('task2_loadFile()')
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

    # process data
    print('check if need to perform postProcessFunc:')
    print(','.join(message.keys()))
    if ('postProcessFunc' in message.keys()):
    #if loadfuncHook in LoadMethod.keys():
        print(' get postProcessFunc() call back')
        #t_func = LoadMethod[loadfuncHook]
        t_func = LoadMethod [message['postProcessFunc']]
        t_func(name,sid)


def load_NGLog(filename, sid):
    start_time = timeit.default_timer()
    cload.loadLogToDb(name, db="sqlite:///{0}/{1}.sqlite".format(DB_FOLDER, sid), new = not addToExistDb)
    print('loadLogToDb: ', timeit.default_timer() - start_time)
    rabbitMq.emit('alert message', {'data': 'New data is available. <a href="/api/pages/{0}">({0})</a>'.format(sid)}, namespace='/test')
    rabbitMq.emit('my response', {'data': 'New data is available. <a href="/api/pages/{0}">({0})</a>'.format(sid)}, namespace='/test')

def load_csvResource(filename, dbid):
    start_time = timeit.default_timer()
    # load to db
    try:
        res = Resource(filename)
    except:
        raise

    # check if there is a df
    dbname = Resource.dbName(dbid)
    if (os.path.exists(dbname)):
        df = Resource.fromDb(dbname).df
        res.pd = pd.concat([df, res.df]).drop_duplicates(inplace=True)
    res.toDB(dbid)
    print('loading time: ', timeit.default_timer() - start_time)
    rabbitMq.emit('alert message', {'data': 'New resource is available. ({0})'.format(dbid)}, namespace='/test')


LoadMethod = {
    'load_NGLog' : load_NGLog,
    'load_csvResource': load_csvResource
}

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
            cload.loadLogToDb(name, db="sqlite:///{0}/{1}.sqlite".format(DB_FOLDER, sid), new = not addToExistDb)
            print('loadLogToDb: ', timeit.default_timer() - start_time)
            rabbitMq.emit('alert message', {'data': 'New data is available. <a href="/api/pages/{0}">({0})</a>'.format(sid)}, namespace='/test')
            rabbitMq.emit('my response', {'data': 'New data is available. <a href="/api/pages/{0}">({0})</a>'.format(sid)}, namespace='/test')
