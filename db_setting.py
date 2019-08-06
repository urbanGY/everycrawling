from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
engine = create_engine('postgresql://superson:superson@superson:5432/crawling', echo=True)
Base = declarative_base()

Session = sessionmaker(engine)
db_session = Session()

def init_db():
    import db.models
    Base.metadata.create_all(engine)
