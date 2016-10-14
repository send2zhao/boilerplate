import os

from flask import url_for, Response, redirect, session, request,render_template
from flask_paginate import Pagination, get_page_args

from .. import db
from ..models import DbFilter
from ..utils import get_datatoken
from .. import cload
from ..ImageViewLog import ImageViewLog, Base

from . import api

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DB_FOLDER = 'db'

"""
Provide the view of the log.
"""
@api.route('/pages', methods=['GET','POST'])
@api.route('/pages/<id>', methods=['GET','POST'])
def pages(id=None):
    print('id:  ({0})'.format(id))
    fdata = session.get('filter', None)
    qid   = session.get('qid', "")
    page  = request.args.get('page', type=int, default=1)
    per_page = 30

    print('fdata: {0}'.format(fdata))
    if (request.method=="POST"):
        fdata = request.form['filter_data']
        if fdata.strip() == '': fdata = None
        session['filter'] = fdata
        if (fdata is not None):
            qid = get_datatoken('{0}-{1}'.format(id,fdata))
            dbFilter = DbFilter(qid, id, fdata)
            # use db session
            with db.session as dbsession:
                if (dbsession.query(DbFilter).filter(qid=qid).first() is None):
                    dbsession.add(dbFilter)
                    dbsession.commit()
            session['qid'] = qid
        return redirect(url_for('api.pages', id = id))

    # sqlite file based
    if id is not None:
        dbfile = '{0}/{1}.sqlite'.format(DB_FOLDER, id)
        if not os.path.exists(dbfile):
            t_db = cload.DB
        else:
            t_db = "sqlite:///{0}/{1}.sqlite".format(DB_FOLDER, id)
    else:
        t_db = cload.DB

    count = 0
    if (fdata is not None):
        try:
            count, imageViewLogs = cload.filterRaw(fdata,
                                     [(page-1)*per_page, (page*per_page)],
                                     db=t_db)
        except:
            print('syntaxError')
            imageViewLogs = []; session['filter'] = None
    else:
        engine = create_engine(t_db)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        dbsession = DBSession()
        count = dbsession.query(ImageViewLog).count()
        imageViewLogs = dbsession.query(ImageViewLog)[(page-1)*per_page:(page*per_page)]
        dbsession.close()
    # pagination is an object to track the pages as well the views of the page icons.
    pagination = Pagination(page=page, total=count, search=False,
                            record_name='pages', per_page =per_page,
                            css_framework = 'bootstrap3')
    return render_template('pages.html',
                           id = id,
                           pages=imageViewLogs,
                           pagination=pagination,
                           filter=fdata,
                           qid = qid,
                           )
