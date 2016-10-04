from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
import os, re

Base = declarative_base()

class ImageViewLog(Base):
    __tablename__ = 'imageViewLog'

    id   = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=True)

    logger = Column(String(255), nullable=True)
    processid = Column(Integer, nullable=True)
    level     = Column(String(32), nullable=True)
    processname = Column(String(255), nullable=True)
    threadid = Column(Integer, nullable=True)
    threadname = Column(String(255), nullable=True)
    machinename = Column(String(255), nullable=True)
    message = Column(String, nullable=True)
    properties = Column(String, nullable=True)


    def __init__(self, data):
        self.time = data['time']
        self.logger= data['logger']

    def getCsvHeader(self):
        return ",".join(['time','logger', 'threadid',
                          'level', 'machinename', 'message'])

    def toCsv(self):
        msg = re.sub("\r?\n", "[LR]", self.message or "")
        msg = re.sub(",", " ", msg)
        word = ",".join([self.time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                        self.logger, str(self.threadid), self.level,
                        self.machinename,
                        msg])
        return word

    def __repr__(self):
        return "<ImageViewLog: {0}>".format(self.time)
