from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from db.db_setting import Base

class Rawdata_movie(Base):
    __tablename__ = 'rawdata_movie'

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

class Review_movie(Base):
    __tablename__ = 'review_movie'

    review_id = Column(Integer, primary_key=True )
    uuid = Column(UUID(as_uuid=True))
    source_site = Column(String(20))
    source_id = Column(String(32), primary_key=True)
    user_name = Column(String(20))
    date = Column(String(32))
    review = Column(String)
    rating = Column(String(10))

    def __init__(self, review_id, uuid, source_site, source_id, user_name, date, review, rating):
        self.review_id = review_id
        self.uuid = uuid
        self.source_site = source_site
        self.source_id = source_id
        self.user_name = user_name
        self.date = date
        self.review = review
        self.rating = rating

#wiki_refineddata
class RefinedData(Base):
    __tablename__ = 'wiki_refineddata'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    page_id = Column(Integer, nullable=True)
    update_date = Column(DateTime(timezone=True))
    data = Column(JSONB)

    def __init__(self, uuid, json):
        self.uuid = uuid
        self.page_id = None
        self.update_date = func.now()
        self.data = json
