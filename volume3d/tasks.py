from . import celery
#from . import db
#from . import socketio


from numpy import random
import time

# connect to the RabbitMQ queue through Kombu
#rabbitMq = socketio.KombuManager('amqp://', write_only = True)

# message_queue used by socketio to communicate
# app=None,
from flask_socketio import SocketIO
rabbitMq = SocketIO(message_queue='amqp://guest@localhost//')


@celery.task
def long_task0(word):
    print('long_task()')


@celery.task
def long_task():
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.5:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        meta = {'current': i, 'total': total, 'status': message}
        time.sleep(0.5)
        if random.random() < 0.5 :
            rabbitMq.emit('my response', {'data': message},
                     namespace='/test')
    rabbitMq.emit('my response', {'data': "long_task completed."},
                     namespace='/test')

@celery.task
def add(x, y):
    return x + y
