from celery_setting import app
import executor

@app.task
def hello():
    print('helllo !')

@app.task
def rawdata_crawling_schedule(): #주기적으로 로우 데이터 테이블에 데이터를 채워넣는다
    # 현재 rawdata에서 중복되지않은 uuid 리스트 추출
    # 해당 uuid의 rawdata insert
    # 해당 uuid의 가장 최신 자료의 조합으로 refine 생성
    print('result')

@app.task
def add_new_movie_schedule(): # 영화 진흥원에서 제공하는 api를 통해 매주 새로 추가되는 영화 데이터를 채워넣는다
    # 영화 감시 모듈
    # 해당 영화 raw_data 에 insert
    # 해당 영화들 refine 만들어서 추가하기
    return 'gg'

@app.task
def data_update_async(): #비동기로 들어오는 특정 터플에 대한 rawdata추가 및 refine 데이터의 업데이트 수행
    # uuid를 전달받는다
    # uuid를 튜플로 만들고 리스트로 감싼다
    # uuid로 영화 identify 불러오기
    # 해당 정보로 raw_data insert
    # 새로운 rawdata 조합으로 refine 데이터 생성
    return 'gg'

#개별 업데이트의 경우에는 uuid를 터플과 리스트로 감싸서 준다
# db_session을 여기로 가져오고 executor는 query로 이름 변경 및 합칠 수 있는 task들을 하나로 모은다.
# 큐 플 사용으로 세션 최적화
