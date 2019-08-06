from sqlalchemy import Column, String
from db.db_setting import Base

class Rawdata(Base):
    __tablename__ = 'rawdata'

    uid = Column(String(36), primary_key=True)
    date = Column(String(12), primary_key=True)
    source_site = Column(String(20), primary_key=True)
    source_id = Column(String(32))
    data = Column(String)
    recovery = Column(String)

    def __init__(self, uid, date, source_site, source_id, data, recovery):
        self.uid = uid
        self.date = date
        self.source_site = source_site
        self.source_id = source_id
        self.data = data
        self.recovery = recovery

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s', '%s', '%s')>" % (self.uid, self.date, self.source_site, self.source_id, self.data, self.recovery)
