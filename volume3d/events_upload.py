from flask import g, session, request
import os
from . import db, socketio, celery
from flask_socketio import join_room, leave_room

from .models import User, File, DbFilter

# global file lists to track all the file-in-part in progress
files         = {}
UPLOAD_FOLDER = 'upload'
namespace     = '/upload'


@socketio.on('upload_fileTest', namespace=namespace)
def upload_fileTest(message):
    sid = request.sid
    print('[upload_fileTest] sid %s' %sid)
    if (message['cmd'] == 1): # new file
        files['sid'] = open(os.path.join(UPLOAD_FOLDER, message['data']), 'wb')
    elif(message['cmd'] == 2):
        files['sid'].write(message['data'])
    else:
        files['sid'].close();
        del files['sid']
        socketio.emit('my response', {'data': "finished loading " + message['data']},
                 namespace=namespace)
