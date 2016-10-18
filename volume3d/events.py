from flask import g, session, request

from . import db, socketio, celery
from flask_socketio import join_room, leave_room

from .models import User, File, DbFilter
import cload
import tasks, task2, task3

DB_FOLDER = "db"

@socketio.on('my event', namespace='/test')
def test_message(message):
    sid = request.sid
    print('[my event ]**test_message** ' + sid)
    socketio.emit('my response', {'data': message['data']}, room=sid,
             namespace='/test')

@socketio.on('my upload event', namespace='/test')
def test_message(message):
    sid = request.sid
    print('**upload file** ' + sid)
    print(message['data'])
    print(message.keys())
    print(message['file'])
    socketio.emit('my response', {'data': message['data']}, room=sid,
             namespace='/test')

@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(message):
    tasks.long_task.delay()
    socketio.emit('my response', {'data': message['data']}, namespace='/test')


@socketio.on('join', namespace='/test')
def join(message):
    sid = request.sid
    task2.long_task2.delay("my words")
    room = message['room']
    join_room(room)
    socketio.emit('my response', {'data': 'Entered room: ' + message['room']},
             room=sid, namespace='/test')


@socketio.on('leave', namespace='/test')
def leave(message):
    sid = request.sid
    #socketio.leave_room(sid, message['room'], namespace='/test')
    room = message['room']
    leave_room(room)
    socketio.emit('my response', {'data': 'Left room: ' + message['room']},
             room=sid, namespace='/test')


@socketio.on('close room', namespace='/test')
def close(message):
    sid = request.sid
    socketio.emit('my response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'], namespace='/test')
    socketio.close_room(message['room'], namespace='/test')


@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    sid = request.sid
    print('send_room_message')
    socketio.emit('my response', {'data': message['data']}, room=message['room'],
             namespace='/test')

@socketio.on('file_upload', namespace='/test')
def file_upload(message):
    sid = request.sid
    print('received file upload blob: %s' % sid)
    filename = message['name']
    fileItem = File(filename, message['data'])
    print(fileItem)
    print(message.keys())
    socketio.emit('my response', {'data': '(sid:{0}) file received, processing...'.format(sid)}, namespace='/test')
    #task2.task2_loadFile.delay(sid, message)
    task2.task2_loadFile.delay(sid, message)


@socketio.on('resource_upload', namespace='/test')
def resource_upload(message):
    sid = request.sid
    print('received resource upload blob: %s', sid)
    filename = message['name']
    fileItem = File(filename, message['data'])
    print(fileItem)
    socketio.emit('my response', {'data': '(sid:{0}) file received, processing...'.format(sid)}, namespace='/test')
    task2.task2_loadFile.delay(sid, message)

@socketio.on('remove dbResource', namespace='/test')
def resource_remove(message):
    sid = request.sid
    print('received resource remove request')
    task2.task2_remove.delay(sid, message)


@socketio.on('export db', namespace="/test")
def export_db(message):
    sid = request.sid
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
    print('emit pushFile event to client')
    socketio.emit("pushFile", {'data': output}, namespace="/test")


@socketio.on('plot request', namespace = "/test")
def receive_plot_request(message):
    print('Processing plot request. %s' %message['dbid'])
    task3.generatePlot.delay(message)
