from . import celery
from flask_socketio import SocketIO

from numpy import random
import time

socketio = SocketIO(message_queue='amqp://')
rabbitMq = socketio

@celery.task
def long_task2(word):
    print('long_task2(): %s' % word)
