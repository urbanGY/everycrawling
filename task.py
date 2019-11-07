from celery_setting import app
import executor
import logging
logging.basicConfig(filename='./log/task.log', format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')


@app.task
def hello(uuid):
    print('helllo',uuid)


@app.task
def rawdata_crawling_schedule():  # 주기적으로 로우 데이터 테이블에 데이터를 채워넣는다
    uuid_list = executor.get_uuid_date_condition('movie')
    input = executor.get_identify(uuid_list)
    executor.insert_rawdata(input)
    executor.update_refined(uuid_list)
    # 현재 rawdata에서 중복되지않은 uuid 리스트 추출
    # 해당 uuid의 rawdata insert
    # 해당 uuid의 가장 최신 자료의 조합으로 refine 생성


@app.task
def data_update_async(uuid, category):  # 비동기로 들어오는 특정 터플에 대한 rawdata추가 및 refine 데이터의 업데이트 수행
    identify = get_identify_use_uuid(uuid, category)
    if identify == None:
        print('identify is null...')
    else :
        source = 'data_update_async'
        identify_list = []
        identify_list.append(identify)
        input = [category, source, identify_list]
        executor.insert_rawdata(input)
        uuid_list = []
        uuid_list.append(uuid)
        input = [category, source, uuid_list]
        executor.update_refined(input)
        print(uuid,'update complete')    


    # uuid로 category와 identify를 받아온다
    # insert raw_data
    # update refine


@app.task
def add_new_movie_schedule():  # 영화 진흥원에서 제공하는 api를 통해 매주 새로 추가되는 영화 데이터를 채워넣는다
    # 영화 감시 모듈
    # 해당 영화 raw_data 에 insert
    # 해당 영화들 refine 만들어서 추가하기
    print('gaga')


# 개별 업데이트의 경우에는 uuid를 터플과 리스트로 감싸서 준다
# 큐 플 사용으로 세션 최적화
