from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy import Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

## http://derrickgilland.com/posts/demystifying-flask-sqlalchemy/
class ModelBase(object):
    """Baseclass for custom user models."""
    query_class = None
    #: an instance of `query_class`. Can be used to query the
    #: database for instances of this model.
    query = None

###

###
class MySqlAlchemy(ModelBase):

    def __init__(self):

        self.Column = Column
        self.Integer= Integer
        self.String = String
        self.DateTime = DateTime
        self.Text   = Text
        self.Boolean= Boolean

        self.url = None

        ##
        self.Model  = declarative_base(cls=ModelBase)
        self.engine = None
        self.Session= sessionmaker()

    def configure(self, config={}):
        print(config)
        if('SQLALCHEMY_DATABASE_URI' not in config.keys()):
            raise ValueError('SQLALCHEMY_DATABASE_URI not available.')
        self.url = config['SQLALCHEMY_DATABASE_URI']

        self.engine = create_engine(self.url, echo=False)
        self.Session.configure(bind=self.engine)

    #Base.metadata.create_all(engine)
    def create_all(self):
        if (self.engine is None):
            raise ValueError('Engine is not ready, please set DATABASE_URL using configure().')
        self.Model.metadata.create_all(self.engine)

    def drop_all(self):
        self.Model.metadata.drop_all()

    from contextlib import contextmanager
    @property
    @contextmanager
    def session(self):
        """
        return a session instance as attribute
        using `with` as example
        with db.session as session:
            session.add(something)
            session.commit()
        """

        session = self.Session()
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
        #return self.Session()
