from . import db
from .utils import timestamp, url_for, get_datatoken

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email    = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %s>' % self.username

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(512))
    token = db.Column(db.String(64), nullable=True, unique=True)
    created_at = db.Column(db.Integer, default=timestamp)
    updated_at = db.Column(db.Integer, default=timestamp, onupdate=timestamp)
    last_seen_at = db.Column(db.Integer, default=timestamp)

    def __init__(self, name, data):
        pass
        self.name = name
        self.token = get_datatoken(data)
        self.last_seen_at = timestamp

    def __repr__(self):
        return '<File name=%s  token=%s>' % ( self.name, self.token)

class DbResource(db.Model):
    """
    Db-Resource management table
    """
    __tablename__ = 'dbResources'
    dbid   = db.Column(db.String(128), primary_key=True)
    dbname = db.Column(db.String(128), nullable=True)
    resourceid = db.Column(db.String(128), nullable=True)

    def __init__(self, dbid, dbname=None, resourceid=None):
        self.dbid   = dbid 
        self.dbname = dbname
        self.resourceid = resourceid

    def __repr__(self):
        return '<DbResource dbname=%s resourceid=%s>' %(self.dbname, self.resourceid)

class DbFilter(db.Model):
    """
    Db and Filter query management table
    """
    __tablename__ = 'dbFilters'
    qid        = db.Column(db.String(128), primary_key=True)
    dbname     = db.Column(db.String(128), nullable=True)
    queryText  = db.Column(db.String(512), nullable=False)


    def __init__(self, qid, db, query):
        self.qid    = qid
        self.queryText  = query
        self.dbname = db

    def __repr__(self):
        return '<DbFilter qid=%s ...>' % (self.qid)
