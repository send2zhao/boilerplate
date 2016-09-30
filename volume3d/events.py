from flask import g, session, request

from . import db, socketio, celery
from flask_socketio import join_room, leave_room

import tasks
import task2


@socketio.on('my event', namespace='/test')
def test_message(message):
    sid = request.sid
    print('**test_message** ' + sid)
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
    filename = message['name']
    print(filename)
    socketio.emit('my response', {'data': 'file received, processing...'}, namespace='/test')
    task2.long_task_loadDBfile.delay(sid, message)
    # do parsing
