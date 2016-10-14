import os

from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from MySqlAlchemy import MySqlAlchemy
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from flask_login import LoginManager

from celery import Celery
from config import config

# Flask extensions
#db        = SQLAlchemy()
db        = MySqlAlchemy()
bootstrap = Bootstrap()
socketio  = SocketIO()
login_manager = LoginManager()
app_config= config['development']

celery = Celery(__name__,
                # if use redis:  'redis://'
                roker=os.environ.get('CELERY_BROKER_URL',   'amqp://guest@localhost//'),
                backend=os.environ.get('CELERY_BROKER_URL', 'amqp://guest@localhost//'))

# Import models so that they are registered with SQLAlchemy
from . import models  # noqa

# Import celery task so that it is registered with the Celery workers
from .tasks import long_task #run_flask_request  # noqa
from .task2 import long_task2,  task2_loadFile
from .task3 import generatePlot

# Import Socket.IO events so that they are registered with Flask-SocketIO
from . import events  # noqa
from . import events_upload

def create_app(config_name=None, main=True):
    if config_name is None:
        config_name = os.environ.get('VOLUME3D_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app_config= config[config_name]


    # Initialize flask extensions
    #db.init_app(app)
    db.configure({'SQLALCHEMY_DATABASE_URI': app.config['SQLALCHEMY_DATABASE_URI']})
    bootstrap.init_app(app)
    login_manager.init_app(app)

    if main:
        # Initialize socketio server and attach it to the message queue, so
        # that everything works even when there are multiple servers or
        # additional processes such as Celery workers wanting to access
        # Socket.IO
        socketio.init_app(app,
                          message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'])
    else:
        # Initialize socketio to emit events through through the message queue
        # Note that since Celery does not use eventlet, we have to be explicit
        # in setting the async mode to not use it.
        socketio.init_app(None,
                          message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
                          async_mode='threading')
    celery.conf.update(config[config_name].CELERY_CONFIG)


    # Register web application routes
    #from .flack import main as main_blueprint
    #app.register_blueprint(main_blueprint)

    # Register API routes
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Register async tasks support
    #from .tasks import tasks_bp as tasks_blueprint
    #app.register_blueprint(tasks_blueprint, url_prefix='/tasks')

    # register the Volume3D, the main
    from .volume3d import main as volume3d_blueprint
    app.register_blueprint(volume3d_blueprint)

    return app
