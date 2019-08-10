import crawler
import uuid
import logging
from time import sleep

from db import db_setting
from db.models import Rawdata #for db function

import json


def log_init(start_date):
    logging.basicConfig(filename='./log/'+start_date+'.log',format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG , datefmt='%Y-%m-%d %H:%M:%S')

def check_uuid(db_session, source_id, uuid):
    query = db_session.query(Rawdata.uuid).filter(Rawdata.source_id == source_id).all()
    print(query)
    for q in query:
        uuid = q[0]
    return uuid

def insert_rawdata():
    log_init('insert_rawdata'+crawler.get_date())
    engine = db_setting.get_rawdata_engine() # create connection to crawling db
    db_session = db_setting.get_sesstion(engine) #create session

    category = 'movie'
    sites = crawler.read_site('all')
    file_name = 'movie_list_1'
    input = crawler.read_input(category, file_name) #'test' to movie_list_<num>

    for movie in input:
        uid = uuid.uuid4()
        sleep(1)
        for site in sites:
            try:
                content_url = crawler.get_url(site, movie)
                raw_data = crawler.get_data(content_url, site)

                source_site = site['site_name']
                source_id = crawler.get_source_id(content_url)
                recovery = crawler.request_recovery(movie, content_url, site)

                entry = Rawdata(uuid = check_uuid(db_session, source_id, uid), source_site = source_site, source_id = source_id, data = raw_data, recovery = recovery)#remove date
                db_session.add(entry)
                db_session.commit()

            except Exception as e:
                logging.error('In '+file_name+' Exception while <'+ site['site_name']+'> searching <'+ movie +'> '+ str(e))
                logging.exception('Got exception')
                logging.error('**********************************')
                continue
    db_session.close()

def get_uuid_list():
    engine = db_setting.get_rawdata_engine() # create connection to crawling db
    db_session = db_setting.get_sesstion(engine) #create session
    list = db_session.query(Rawdata.uuid).group_by(Rawdata.uuid).all()
    db_session.close()
    return list #튜플 반환형임;

def insert_refined(uuid_list):
    log_init('insert_refined'+crawler.get_date())
    from sqlalchemy import and_
    from sqlalchemy.sql import func
    engine = db_setting.get_rawdata_engine() # create connection to crawling db
    db_session = db_setting.get_sesstion(engine) #create session
    # must be for uuid list , 개별 업데이트 시에는 uuid 넣기전에 리스트로 한번 감싸서 ㄱ ㄱ
    for uuid in uuid_list:
        try:
            sub = db_session.query(func.max(Rawdata.date).label('lastdate')).filter(Rawdata.uuid == uuid).group_by(Rawdata.source_site).subquery('sub')
            ans = db_session.query(Rawdata.source_site, Rawdata.data, Rawdata.recovery).filter(and_(Rawdata.date == sub.c.lastdate)).all()
            json_form = crawler.make_json(uuid,ans) #완성된 제이슨 데이터!

        except Exception as e:
            logging.error('In uuid :  '+uuid+' Exception ' + str(e))
            logging.exception('Got exception')
            logging.error('**********************************')
            continue
    db_session.close()

insert_rawdata()
#insert_refined(['37a88b3d-340e-406b-a62a-3ac45c0c7c56'])
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   sql -> 해당 하는 uuid를 가진 터플 중에 가장 최근에 업데이트 된 사이트별 사이트명과 데이터를 가져와야한다                      #
#   select source_site, data                                                                                #
#   from rawdata                                                                                            #
#   where rawdata.date = (select max(date) from rawdata where rawdata.uuid == uuid group by source_site)    #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#TODO : 데이터 하나로 합치는 모듈, 테스트 코드들 모두 작성하기
#insert_rawdata()
#get_uuid_list()

#db_setting.create_rawdata_table(db_setting.get_rawdata_engine())

#영화 리스트 감시하는 모듈 작성 필요
#레디스 자동 세팅
#시간 확인, 아마존 인스턴스의 시간을 세팅할 수 있는가?
#제이슨으로 하나로 합치는 모듈
#포스터 유알엘 별도로 가져오는 모듈
#현재 모든 모듈들에대한 테스트 코드 작성하기
