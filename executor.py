import crawler
import uuid
import logging
from time import sleep

from db import db_setting
from db.models import Rawdata_movie, RefinedData, Review_movie #for db function

import json

def create_table():
    engine = db_setting.get_rawdata_engine()
    # db_setting.create_rawdata_table(engine)
    db_setting.create_review_table(engine)


#****************************** log *************************************
def log_init(start_date):
    logging.basicConfig(filename='./log/'+start_date+'.log',format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG , datefmt='%Y-%m-%d %H:%M:%S')

#****************************** local file input *************************************
def get_input_list(category, file_name):
    input = crawler.read_input(category, file_name) #'test' to movie_list_<num>
    return [category, file_name, input]

#****************************** get category use uuid ************************************* !!
def get_category_uuid(uuid):
    #refine에서 카테고리를 가져옴
    return ['category','source','uuid']

#****************************** get uuid *************************************
def get_uuid_list_all(category): #존재하는 모든 중복되지 않은 uuid를 rawdata __tablename__에서 가져옴
    engine = db_setting.get_rawdata_engine() # create connection to crawling db
    db_session = db_setting.get_sesstion(engine) #create session
    uuid_list = db_session.query(Rawdata_movie.uuid).group_by(Rawdata_movie.uuid).all()
    #해당하는 카테고리의 테이블에서 모든 uuid를 가져옴
    db_session.close()
    return [category, 'from get_uuid_lsit_all', uuid_list] #튜플 반환형임;

def get_uuid_refine(category): #refine 테이블에 있는 모든 uuid를 가져 **!! TODO : 나중에 모두 가져오는게 아니라 특정 카테고리를 가져오는 것으로 변경해야한다!
    refine_engine = db_setting.get_refineddata_engine()
    refine_db_session = db_setting.get_sesstion(refine_engine)
    uuid_list = refine_db_session.query(RefinedData.uuid).all()
    refine_db_session.close()
    return [category, 'from get_uuid_refine', uuid_list]

def get_uuid_refine_notexist_review(category):
    from sqlalchemy.sql import func
    refine_engine = db_setting.get_refineddata_engine()
    refine_db_session = db_setting.get_sesstion(refine_engine)
    rawdata_engine = db_setting.get_rawdata_engine() # create connection to crawling db
    rawdata_db_session = db_setting.get_sesstion(rawdata_engine) #create session

    sub = rawdata_db_session.query(Rawdata_movie.uuid).group_by(Rawdata_movie.uuid).all()
    uuid_list = refine_db_session.query(RefinedData.uuid).filter(RefinedData.uuid.notin_(sub)).all()
    rawdata_db_session.close()
    refine_db_session.close()
    return [category, 'from get_uuid_refine', uuid_list]

def get_uuid_not_exist(category): #refine table에 없는 중복되지않은 모든 uuid를 가져옴
    rawdata_engine = db_setting.get_rawdata_engine() # create connection to crawling db
    rawdata_db_session = db_setting.get_sesstion(rawdata_engine) #create session
    refine_engine = db_setting.get_refineddata_engine()
    refine_db_session = db_setting.get_sesstion(refine_engine)

    refine_list = refine_db_session.query(RefinedData.uuid).all()
    raw_list = rawdata_db_session.query(Rawdata_movie.uuid).group_by(Rawdata_movie.uuid).all()
    # refine에서 카테고리가 일치하는 uuid만 가져오게해서 연산하게 만듬, 밑의 rawdata는 radata_+category로 테이블을 식별하게 만듬
    rawdata_db_session.close()
    refine_db_session.close()

    new_uuid_list = list(set(raw_list) - set(refine_list))
    return [category, 'from get_uuid_not_exist', new_uuid_list]

def get_uuid_date_condition(category): #한달 전꺼면 해당 uuid 모두 소집
    from datetime import datetime, timedelta
    from sqlalchemy.sql import func
    thirty_days_ago = func.now() - timedelta(days = 30)

    refine_engine = db_setting.get_refineddata_engine()
    refine_db_session = db_setting.get_sesstion(refine_engine)
    uuid_list = refine_db_session.query(RefinedData.uuid).filter(RefinedData.update_date <= thirty_days_ago).all()
    # refine의 json category와 카테고리가 일치하는 uuid만 가져오기로 사용
    refine_db_session.close()
    return [category, 'from get_uuid_date_condition',uuid_list]

# def get_source_and_id(uuid): #source 와 source_id 값을 uuid를 찾아 반환해준다 / 독립적으로 수행할 수 있음
#     rawdata_engine = db_setting.get_rawdata_engine() # create connection to crawling db
#     rawdata_db_session = db_setting.get_sesstion(rawdata_engine) #create session
#     source_list = rawdata_db_session.query(Rawdata_movie.source_site, Rawdata_movie.source_id).filter(Rawdata_movie.uuid == uuid).all()
#     rawdata_db_session.close()
#     return source_list



#****************************** get identify use uuid *************************************
def get_identify(uuid_list): #uuid 튜플 리스트를 주면 identify 리스트를 반환한다.
    rawdata_engine = db_setting.get_rawdata_engine() # create connection to crawling db
    rawdata_db_session = db_setting.get_sesstion(rawdata_engine) #create session

    category = uuid_list[0] #후에 이걸 이용해서 Rawdata_+category 형식으로 테이블 구분해 데이터 가져오기
    source = uuid_list[1]
    uuid_list  = uuid_list[2]

    identify_list = []
    for uuid in uuid_list:
        uuid = uuid[0]
        ans = rawdata_db_session.query(Rawdata_movie.recovery).filter(Rawdata_movie.uuid == uuid).first()
        identify = ans[0][1]
        identify_list.append(identify)
    rawdata_db_session.close()
    return [category, 'uuid_to_identify', identify_list]

#****************************** insert rawdata_table *************************************
def check_uuid(db_session, source_id, uuid): #기존에 같은 sourceid가 있는지 확인해서 있으면 기존 uuid를 반환
    query = db_session.query(Rawdata_movie.uuid).filter(Rawdata_movie.source_id == source_id).all()
    for q in query:
        uuid = q[0]
    return uuid

def insert_rawdata(input):
    log_init('insert_rawdata'+crawler.get_date())
    engine = db_setting.get_rawdata_engine() # create connection to crawling db
    db_session = db_setting.get_sesstion(engine) #create session

    sites = crawler.read_site('all')
    category = input[0]
    source = input[1]
    input = input[2]

    for movie in input:
        uid = uuid.uuid4()
        sleep(1)
        for site in sites:
            try:
                content_url = crawler.get_url(site, movie)
                raw_data = crawler.get_raw_data(content_url)

                source_site = site['site_name']
                source_id = crawler.get_source_id(content_url)
                recovery = crawler.request_recovery(category, movie, content_url, site)

                entry = Rawdata_movie(uuid = check_uuid(db_session, source_id, uid), source_site = source_site, source_id = source_id, data = raw_data, recovery = recovery)#remove date
                db_session.add(entry)
                db_session.commit()

            except Exception as e:
                logging.error('In '+source+' Exception while <'+ site['site_name']+'> searching <'+ movie +'> '+ str(e))
                logging.exception('Got exception.. ')
                logging.error('**********************************')
                continue
    db_session.close()

#****************************** insert refine_table *************************************
def insert_refined(uuid_list):
    log_init('insert_refined'+crawler.get_date())
    from sqlalchemy import and_
    from sqlalchemy.sql import func

    rawdata_engine = db_setting.get_rawdata_engine() # create connection to crawling db
    rawdata_db_session = db_setting.get_sesstion(rawdata_engine) #create session
    refine_engine = db_setting.get_refineddata_engine()
    refine_db_session = db_setting.get_sesstion(refine_engine)
    # must be for uuid list , 개별 업데이트 시에는 uuid 넣기전에 리스트로 한번 감싸서 ㄱ ㄱ

    category = uuid_list[0]
    source = uuid_list[1]
    uuid_list = uuid_list[2]

    for uuid in uuid_list:
        try:
            uuid = uuid[0]
            sub = rawdata_db_session.query(func.max(Rawdata_movie.date).label('lastdate')).filter(Rawdata_movie.uuid == uuid).group_by(Rawdata_movie.source_site).subquery('sub')
            ans = rawdata_db_session.query(Rawdata_movie.source_site, Rawdata_movie.data, Rawdata_movie.recovery).filter(and_(Rawdata_movie.date == sub.c.lastdate)).all()
            json_form = crawler.make_json(str(uuid),ans) #완성된 제이슨 데이터!
            entry = RefinedData(uuid, json_form)
            refine_db_session.add(entry)
            refine_db_session.commit()
        except Exception as e:
            logging.error('In uuid :  '+str(uuid)+' Exception ' + str(e))
            logging.exception('Got exception.. ')
            logging.error('**********************************')
            continue
    rawdata_db_session.close()
    refine_db_session.close()

def update_refined(uuid_list):
    log_init('update_refined'+crawler.get_date())
    from sqlalchemy import and_
    from sqlalchemy.sql import func

    rawdata_engine = db_setting.get_rawdata_engine() # create connection to crawling db
    rawdata_db_session = db_setting.get_sesstion(rawdata_engine) #create session
    refine_engine = db_setting.get_refineddata_engine()
    refine_db_session = db_setting.get_sesstion(refine_engine)
    # must be for uuid list , 개별 업데이트 시에는 uuid 넣기전에 리스트로 한번 감싸서 ㄱ ㄱ

    category = uuid_list[0]
    source = uuid_list[1]
    uuid_list = uuid_list[2]

    for uuid in uuid_list:
        try:
            uuid = uuid[0]
            sub = rawdata_db_session.query(func.max(Rawdata_movie.date).label('lastdate')).filter(Rawdata_movie.uuid == uuid).group_by(Rawdata_movie.source_site).subquery('sub')
            ans = rawdata_db_session.query(Rawdata_movie.source_site, Rawdata_movie.data, Rawdata_movie.recovery).filter(and_(Rawdata_movie.date == sub.c.lastdate)).all()
            json_form = crawler.make_json(str(uuid),ans) #완성된 제이슨 데이터!
            refine = refine_db_session.query(RefinedData).filter(RefinedData.uuid == uuid).one()
            refine.data = json_form
            refine.update_date = func.now()
            refine_db_session.commit()
        except Exception as e:
            logging.error('In uuid :  '+str(uuid)+' Exception ' + str(e))
            logging.exception('Got exception.. ')
            logging.error('**********************************')
            continue
    rawdata_db_session.close()
    refine_db_session.close()

def insert_review_test(category, source_site):
    from sqlalchemy import and_
    log_init('insert_review_test'+crawler.get_date())
    rawdata_engine = db_setting.get_rawdata_engine() # create connection to crawling db
    rawdata_db_session = db_setting.get_sesstion(rawdata_engine) #create session

    elem = get_uuid_refine_notexist_review(category)
    uuid_list = elem[2] #[(UUID('asdfasdf',)),(UUID('asdfasdf',))] 이런꼴로 나옴
    for uuid in uuid_list:
        uuid = uuid[0]
        source_list = rawdata_db_session.query(Rawdata_movie.source_id).filter(and_(Rawdata_movie.uuid == uuid, Rawdata_movie.source_site == source_site)).group_by(Rawdata_movie.source_id).all() #쿼리 수정, 디비백업 쉘스크립트
        for source in source_list:
            source_id = source[0]
            if source_site == 'naver_movie':
                review_list = crawler.get_naver_review(source_id)
            elif source_site == 'watcha':
                review_list = crawler.get_watcha_review(source_id)
            elif source_site == 'daum_movie':
                review_list = crawler.get_daum_review(source_id)
            elif source_site == 'maxmovie':
                review_list = crawler.get_maxmovie_review(source_id)
            bulk_object = []
            review_id = 0
            for data in review_list:
                review_id += 1
                user_name = data[0]
                review = data[1]
                date = data[2]
                rating = data[3]
                entry = Review_movie(review_id = review_id, uuid = uuid, source_site = source_site, source_id = source_id, user_name = user_name, date = date, review = review, rating = rating )#remove date
                # try:
                #     rawdata_db_session.add(entry)
                #     rawdata_db_session.commit()
                # except Exception as e:
                #     logging.error('In uuid :  '+str(uuid)+' Exception ' + str(e))
                #     logging.exception('Got exception.. ')
                #     logging.error('**********************************')
                #     continue
                bulk_object.append(entry)
            try :
                rawdata_db_session.bulk_save_objects(bulk_object)
                rawdata_db_session.commit()
            except Exception as e:
                logging.error('In uuid :  '+str(uuid)+' Exception ' + str(e))
                logging.exception('Got exception.. ')
                logging.error('**********************************')
                continue

    rawdata_db_session.close()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   sql -> 해당 하는 uuid를 가진 터플 중에 가장 최근에 업데이트 된 사이트별 사이트명과 데이터를 가져와야한다                      #
#   select source_site, data                                                                                #
#   from rawdata                                                                                            #
#   where rawdata.date = (select max(date) from rawdata where rawdata.uuid == uuid group by source_site)    #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#테이블 만들기
create_table()

# 전체 중복되지않은 raw_data의 uuid 가져오기 (select)
#uuid_list = get_uuid_list_all('movie')
#update_refined(uuid_list)

### 그냥 새로운 rawdata 처음으로 movie_list_ 에서 읽어와 채워 넣을 때 (insert)
# for i in range(30,50):
#     file = 'movie_list_'+str(i)
#     input = get_input_list('movie', file)
#     insert_rawdata(input)

# raw_data에는 있지만 refine 되지 않은 데이터를 refine 테이블에 채워 넣을 때 (insert)
# uulist = get_uuid_not_exist('movie')
# insert_refined(uulist)

# 특정 날짜 조건의 uuid 리스트 가져오기 (ex) update date가 특정 시간 이하일 경우 가져온다) (select)
#uuid_list = get_uuid_date_condition('movie')

# 스케줄링된 기존 raw_data 인서트, refine에 업데이트 (update)
#uuid_list = get_uuid_date_condition('movie')
#input = get_identify(uuid_list)
#insert_rawdata(input)
#update_refined(uuid_list)

# 비동기로 들어온 특정 rawdata에 대한 인서트 + refine에 해당 업데이터 반영 (update)
#uuid_list = uuid 여기에 카테고리, 출처, uuid 순서로 감싸야됨
#uu = '5d25d66a-e51c-402e-995e-d761508b8b8b'
#uuid_list = ['movie','gg',[((uu),)]]
# input = get_identify(uuid_list)
# insert_rawdata(input)
#update_refined(uuid_list)

# uuid를 통해서 이미 입력된 identify 가져오는 모듈 만들기
#get_identify(uuid_list) 터플과 리스트로 둘러싼 uuid리스트

#!@#@!#!@#@!#!#!@#@!#!#!@# 여기서 부터 다시 시작
# reine 에서 uuid 가져오기
# elem = get_uuid_refine('movie')
# uuid_list = elem[2]
# t_uuid = uuid_list[0][0]
# source_list = get_source_and_id(t_uuid)
# print(source_list)
#insert_review_test('movie','naver_movie')
#insert_review_test('movie','watcha')
#insert_review_test('movie','daum_movie')
#insert_review_test('movie','maxmovie')

# find json attrib query
#SELECT *
#FROM public.wiki_refineddata
#WHERE public.wiki_refineddata.data -> 'data' ->> 'title' = '라이온 킹'

# ** bulk update method!!
# s = Session()
# objects = [
#     User(name="u1"),
#     User(name="u2"),
#     User(name="u3")
# ]
# s.bulk_save_objects(objects)
# s.commit()



#celery redis 모듈 작성하기
#영화 리스트 감시하는 모듈 작성 필요
#레디스 자동 세팅
#시간 확인, 아마존 인스턴스의 시간을 세팅할 수 있는가?
#포스터 유알엘 별도로 가져오는 모듈 #네이버가 안될 경우 필요함
#현재 모든 모듈들에대한 테스트 코드 작성하기.. 계속 진행 ㄱㄱ
#rawdata_movie 로 테이블 제작
# sqlalchemy bulk update
# maxmovie 매트릭스 레볼루션 같은 경우에 xpath에서 경로상의 div 위치가 바뀜! 따라서 검색이 되었음에도 영화 파트가 아닌 뉴스 파트에서 코드가 작동해 크롤링을 못해오는중
