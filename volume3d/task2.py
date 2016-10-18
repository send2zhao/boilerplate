"""
The celery workers are in the same machine.
If need to run worker in the different machine, see
    `http://avilpage.com/2014/11/scaling-celery-sending-tasks-to-remote/`
The bottle necks are:
    configuration, and
    resource sharing.

An alternative solution is to run the web server on multiple machines. each
has some number of workers. This solution resolves the configuration/code sharing
between the web app and the celery worker. However, the sharing resource, such
as data still needs to be considered.
"""

from . import celery, app_config
from numpy import random
import time,timeit, sys, os, uuid

import cload
from Resource import Resource
from models import DbResource

# a seperate socket server
from flask_socketio import SocketIO
rabbitMq = SocketIO(message_queue='amqp://', async_mode = 'threading')

# a seperate salAlchemy connect
from MySqlAlchemy import MySqlAlchemy
db = MySqlAlchemy()
db.configure({'SQLALCHEMY_DATABASE_URI': app_config.SQLALCHEMY_DATABASE_URI})

DB_FOLDER = "db"

@celery.task
def long_task2(word):
    print('long_task2(): %s' % word)
    rabbitMq.emit('my response', {'data': 'I am finished the long_task2()'},
             namespace='/test')


@celery.task
def task2_remove(sid, message):
    pass
    if ('dbid'in message):
        remove_dbResource(message['dbid'], dtype=message['dbtype'])
    else:
        print('task2_remove: no dbid')


def remove_dbResource(dbid, dtype='NGLog'):
    pass
    if (dtype == 'NGLog'):
        dbfile = os.path.join(DB_FOLDER, '{0}.sqlite'.format(dbid))
    else:
        dbfile = os.path.join(DB_FOLDER, '{0}.pickle'.format(dbid))
    if (os.path.exists(dbfile)):
        os.unlink(dbfile)

    with db.session as dbsession:
        dbResource = dbsession.query(DbResource).filter_by(dbid=dbid).first()
        del_record = False
        if (dbResource):
            if (dtype=='NGLog'):
                dbResource.ivlog = False
            else:
                dbResource.hwlog = False
            if (not dbResource.ivlog) and (not dbResource.hwlog):
                dbsession.delete(dbResource)
                del_record = True
            dbsession.commit()
            if (del_record):
                rabbitMq.emit('remove row', {'dbid': dbid}, namespace='/test')


@celery.task
def task2_loadFile(sid, message):
    """
    sid: request sid
    message: expect
    """
    print('task2_loadFile()')
    rabbitMq.emit('my response', {'data': 'processing ...'}, namespace='/test')

    if ('numBlob' in message.keys()):
        sid = message['sid']
        print('sid: %s' %sid)
        folder = os.path.join('upload', sid)
        name   = os.path.join('upload', "{0}.{1}".format(message['sid'], message['blobId']))
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
    if ('postProcessFunc' in message):
        print(' get postProcessFunc() call back')
        print(message['postProcessFunc'])
        t_func = LoadMethod [message['postProcessFunc']]
        dbid = message['dbid']
        if (dbid == 0): # create a valid dbid if it is invalid (0)
            dbid = uuid.uuid1().hex
        rabbitMq.emit('my response', {'data': 'dbid: {0}'.format(dbid)}, namespace='/test')
        t_func(name, dbid)

def load_NGLog(filename, dbid):
    """
    Load NG Log file into the database
    """
    print('log_NGLog()')
    start_time = timeit.default_timer()
    try:
        # check if it alreay exists
        with db.session as dbsession:
            dbResource = dbsession.query(DbResource).filter_by(dbid = dbid).first()
        if (dbResource is None):
            print('add a new entry in DbResource table. %s' %dbid)
            dbResource = DbResource(dbid)
            dbsession.add(dbResource)
            dbsession.commit()

        state = cload.loadLogToDb(filename,
                          db  = "sqlite:///{0}/{1}.sqlite".format(DB_FOLDER, dbid),
                          new = not os.path.exists(os.path.join(DB_FOLDER, '{0}.sqlite'.format(dbid))))
        if (state['success']):
            with db.session as dbsession:
                dbResource = dbsession.query(DbResource).filter_by(dbid = dbid).first()
                dbResource.ivlog = True
                dbResource.machinename = state['machinename']
                dbsession.commit()
    except:
        print ("Unexpected error:", sys.exc_info())
        raise


    print('loadLogToDb: ', timeit.default_timer() - start_time)
    rabbitMq.emit('alert message', {'data': u'New data is available. <a href="/api/pages/{0}">({0})</a>'.format(dbid)}, namespace='/test')
    rabbitMq.emit('my response', {'data': u'New data is available. <a href="/api/pages/{0}">({0})</a>'.format(dbid)}, namespace='/test')

def load_csvResource(filename, dbid):
    start_time = timeit.default_timer()
    # load to db
    # check if it alreay exists
    with db.session as dbsession:
        dbResource = dbsession.query(DbResource).filter_by(dbid = dbid).first()
        if (dbResource is None):
            dbsession.add(DbResource(dbid))
            dbsession.commit()

    try:
        print(filename)
        res = Resource(logfile=filename)
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        raise
    except ValueError:
        print ("Could not convert data to an integer.")
        raise
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise

    # check if there is a df
    dbname = Resource.dbName(dbid)
    dbname = os.path.join(DB_FOLDER, dbname)
    print('check if a db already exist. %s' %dbname)
    if (os.path.exists(dbname)):
        df = Resource.fromDb(dbname).df
        res.df = pd.concat([df, res.df]).drop_duplicates(inplace=True)
    print('dump to file')
    res.toDB(dbid, folder=DB_FOLDER)

    with db.session as dbsession:
        dbResource = dbsession.query(DbResource).filter_by(dbid = dbid).first()
        if (dbResource is not None):
            #dbResource.resourceid = dbid
            dbResource.hwlog = True
            dbsession.commit()

    print('loading time: ', timeit.default_timer() - start_time)
    rabbitMq.emit('alert message', {'data': 'New resource is available. ({0})'.format(dbid)}, namespace='/test')

## Functions that load different types of files
LoadMethod = {
    'load_NGLog' : load_NGLog,
    'load_csvResource': load_csvResource,
}
