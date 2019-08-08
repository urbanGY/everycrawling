from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from db.db_setting import Base

class Rawdata(Base):
    __tablename__ = 'rawdata'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    date = Column(DateTime(timezone=True), default=func.now(), primary_key=True)
    source_site = Column(String(20), primary_key=True)
    source_id = Column(String(32))
    data = Column(String)
    recovery = Column(String)

    def __init__(self, uuid, source_site, source_id, data, recovery):
        self.uuid = uuid
        self.date = func.now()
        self.source_site = source_site
        self.source_id = source_id
        self.data = data
        self.recovery = recovery

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s', '%s', '%s')>" % (self.uuid, self.date, self.source_site, self.source_id, self.data, self.recovery)

#wiki_refineddata
class RefinedData(Base):
    __tablename__ = 'wiki_refineddata'

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True))
    page_id = Column(Integer)
    update_date = Column(DateTime(timezone=True))
    json = Column(JSONB)

    def __init__(self, uuid, page_id, json):
        self.id = ''
        self.uuid = uuid
        self.page_id = page_id
        self.update_date = func.now()
        self.json = json
