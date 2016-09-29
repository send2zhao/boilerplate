from flask import g, session, request

from . import db, socketio, celery

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
    #task2.long_task2("my words")
    socketio.enter_room(sid, message['room'], namespace='/test')
    socketio.emit('my response', {'data': 'Entered room: ' + message['room']},
             room=sid, namespace='/test')


@socketio.on('leave', namespace='/test')
def leave(message):
    sid = request.sid
    socketio.leave_room(sid, message['room'], namespace='/test')
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
def send_room_message(sid, message):
    print('send_room_message')
    socketio.emit('my response', {'data': message['data']}, room=message['room'],
             namespace='/test')
