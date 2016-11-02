from numpy import random
import time,timeit, sys, os, uuid

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from . import celery, app_config
from models import DbFilter
import cload
from makeImageViewLogPlot import makeImageViewLogPlot

# a seperate salAlchemy connect
from MySqlAlchemy import MySqlAlchemy
db = MySqlAlchemy()
db.configure({'SQLALCHEMY_DATABASE_URI': app_config.SQLALCHEMY_DATABASE_URI})
DB_FOLDER = "db"

DBPLOT_FOLDER = 'volume3d/static/dbplot'

from flask_socketio import SocketIO
rabbitMq = SocketIO(message_queue='amqp://', async_mode = 'threading')

@celery.task
def generateQueryPlot(message):

    #sid = request.sid
    print(message)
    with db.session as dbsession:
        queryFilter = dbsession.query(DbFilter).filter_by(qid = message['qid']).first()

    #queryFilter = DbFilter.query.filter_by(qid = message['qid']).first()
    dbname = queryFilter.dbname or "01234"
    t_db = "sqlite:///{0}/{1}.sqlite".format(DB_FOLDER, dbname)
    print('db: ', t_db)
    print('query:  ', queryFilter.queryText)
    count, imageViewLogs = cload.filterRaw(queryFilter.queryText, db=t_db)

    words = [x.toCsv() for x in imageViewLogs]
    output= "\n".join([imageViewLogs[0].getCsvHeader()] + words)

    htmlfile  = '{0}.html'.format(message['qid'])
    htmlfile  = os.path.join(DBPLOT_FOLDER, htmlfile)
    queryInfo = {'table': dbname,
                 'query': queryFilter.queryText}
    try:
        makeImageViewLogPlot(StringIO(output), htmlfile, queryInfo)
    except:
        print('error while running makeImageViewLogPlot()')
    finally:
        pass
    print('emit dbplotReady event.')
    rabbitMq.emit('dbplotReady',
                 {'data': u'Data plot is available. <a href="/static/dbplot/{0}.html">({0})</a>'.format(message['qid'])},
                  room = message['sid'],
                  namespace='/test')
