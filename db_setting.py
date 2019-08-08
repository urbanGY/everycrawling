from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_rawdata_engine():
    engine = create_engine('postgresql://superson:superson@superson:5432/crawling', echo=True)
    return engine

def get_refineddata_engine():
    engine = create_engine('postgresql://superson:superson@superson:5432/Everyreview', echo=True)
    return engine

def get_sesstion(engine):
    Session = sessionmaker(engine)
    db_session = Session()
    return db_session

def create_rawdata_table(engine):
    import db.models
    Base.metadata.create_all(engine)
