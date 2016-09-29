#!/usr/bin/python
# -*- coding: utf-8 -*-

#Test python concurrent

"""
Assume:
datetime format: 2016-09-21 15:11:11.8967 (2016-09-21 15:11:11.0067)
"""


import os, sys
import timeit
import re
from datetime import datetime

FILENAME=r"c:/temp/TraceLog_2016-09-21.47.xrslog"
DB      =r"sqlite:///orm_in_detail.sqlite"

from kitchen.text.converters import to_bytes, to_unicode
import codecs
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ImageViewLog import ImageViewLog, Base

def loadLogToDb(filename, db, startline = 1, new = False):
    data = loadLog(filename)
    lct, record = parseLog(data, startline)
    if (lct != len(data)):
        print('[WARNING] Last line # {0} (total entry {1}).'.format(lct, len(data)))
    # sqlite file based
    engine = create_engine(db)
    if (new):
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    engine.execute(ImageViewLog.__table__.insert(),record)


def loadLog(filename):
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        data = f.readlines()
    return data

def parseLog(lines, start, end=None):
    if (end is None) : end = len(lines)

    entry = []
    i = start
    while (i < end):
        i, ret = getContent(lines, i)
        if (ret is not None):
            entry.append(ret)
    return i, entry

def getContent(lines, i):
    #print(u"{0} {1}\n".format(i, lines[i]).encode("utf-8"))
    #print(lines[1])
    #print(u"中文")
    #print(to_unicode(lines[1]))

    values = lines[i].split(u'§')
    info = []
    ret  = {}
    ret['lineNum']    = i
    #ret['time']       = datetime.strptime(values[1], '%Y-%m-%d %H:%M:%S.%f')#values[1]
    ret['time']       = datetime(*map(int, re.split("[, -.:]+", values[1]+'00')))
    ret['logger']     = values[2]
    ret['level']      = values[3]
    ret['processid']  = values[4]
    ret['processname']= values[5]
    ret['threadid']   = int(values[6])
    ret['threadname'] = values[7]
    ret['machinename']= values[8]
    ret['properties'] = ''

    if (len(values) == 11):
        ret['properties'] = values[-1]
        info.append(values[-2])
    elif (len(values)==10):
        info.append(values[-1])

    while (True):
        i = i + 1
        if (len(lines)<=i):
            break
        if re.match(u"^0§",lines[i]):
            break
        info.append(lines[i])

    if (len(info)>1): # parse out the
        values   = info[-1].split(u'§')
        info[-1] = values[0]
        ret['properties'] = values[-1]

    ret['message'] = u''.join(info)
    return (i, ret)


def query(db=None):
    # sqlite file based
    if db is None:
        db = DB
    engine = create_engine(db)
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(ImageViewLog).filter(ImageViewLog.level.like("%"+"Error"+"%")).order_by(ImageViewLog.time).order_by(ImageViewLog.logger)
    #for item in items:
    #    print(item.time, item.message)
    session.close()
    return items

from sqlalchemy import text

def filterRaw(sqlstm, range, db=None):
    if db is None : db = DB
    engine = create_engine(db)
    items = []
    count = 0
    try:
        output = []
        sql = r'SELECT id from imageViewLog ' + sqlstm
        print (sql)
        try:
            with engine.connect() as con:
                rs = con.execute(text(sql))
                for row in rs:
                    output.append(row[0])
        except:
            print "--------------------"
            output = []
            raise SyntaxError()
        count = len(output)
        if (range[1]>count): range[1] = count
        if (range[0]>count): range[0] = count
        output = output[range[0]:range[1]]

        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        print('[WARNING] trucate to 1000 elements')
        items = session.query(ImageViewLog).filter(ImageViewLog.id.in_(output)).all()
        session.close()
    except:
        items=[]
        print('ERROR')
        raise SyntaxError()
    return count, items


if __name__ == "__main__":
    print("Load files.")
    start_time = timeit.default_timer()
    data = loadLog(FILENAME)
    print('Load log: ', timeit.default_timer() - start_time)

    start_time = timeit.default_timer()
    lct, record = parseLog(data, 1)
    print('Parse log: ', timeit.default_timer() - start_time)

    print(lct, len(record))
    #print(u''.join(record[5]['message']))
    print(record[5]['message'])
    print(u"properties: %s" %record[5]['properties'])

    # sqlite file based
    engine = create_engine(DB)

    # sqlite in memory
    #engine = create_engine('sqlite://')
    # postgresql
    #dialect+driver://username:password@host:port/database
    #engine = create_engine('postgresql://hui:zhaohui@localhost/mydatabase')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    #Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    start_time = timeit.default_timer()
    engine.execute(ImageViewLog.__table__.insert(),record)
    print('Add to db: ', timeit.default_timer() - start_time)

    items = session.query(ImageViewLog).first()
    print(items.time, items.message)

    items = session.query(ImageViewLog).filter(
        ImageViewLog.time < datetime(2016,9,21, 15, 11, 11, 9000))

    items = session.query(ImageViewLog).filter(ImageViewLog.level.like("%"+"Error"+"%")).order_by(ImageViewLog.time).order_by(ImageViewLog.logger)
    for item in items:
        print(item.time, item.message)

    print('-----')
    start_time = timeit.default_timer()
    items = filterRaw('WHERE logger LIKE "%Eclipse%" AND time > "2016-09-21 15:12:00"  LIMIT 10')
    print('query: ', timeit.default_timer() - start_time)
    for item in items:
        print(item.time, item.logger)

    start_time = timeit.default_timer()
    loadLogToDb(FILENAME, DB, new = True)
    print('loadLogToDb: ', timeit.default_timer() - start_time)
