from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import json
from collections import OrderedDict
import datetime
import time
#import requests
import psycopg2

# Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
def remove_blank(s): #입력 스트링의 공백 제거
    remove = ''
    for c in s:
        if c == '\n' or c == '(': # 보통 괄호는 한글 제목의 영문을 표기하기위해 쓰임으로 필터링 결정
            break;
        if c != ' ':
            remove += c
    return remove

def init():
    chrome_option = webdriver.ChromeOptions() #headless 옵션 객체 생성
    chrome_option.add_argument('--headless')
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('--disable-dev-shm-usage')
    chrome_option.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
    driver = webdriver.Chrome('/app/everycrawling/chromedriver', options=chrome_option) #chrome driver 사용 및 headless 옵션 객체 적용
    driver.implicitly_wait(3) #랜더링 완료 시간 대기
    return driver

def init_firefox():
    firefox_option = Options()
    firefox_option.add_argument("--headless")
    driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver',firefox_options=firefox_option)
    print('driver ready')
    driver.implicity_wait(3)
    print('return driver')
    return driver

def read_site_list():
    # f = open('data/movie/site_list.json',mode='r',encoding='utf-8')
    f = open('site/site_list.json',mode='r',encoding='utf-8')
    json_site = json.load(f)
    site_list = json_site['site_list']
    f.close()
    return site_list

def read_movie_list(num):
    # f = open('data/movie/input/test.txt',mode='r',encoding='utf-8')
    f = open('movielist/movie_list_'+num+'.txt',mode='r',encoding='utf-8')
    movie_list = []
    while True:
        line = f.readline()
        if not line:
            break
        _, cid, title, contry, open_year, start_year = line.split('|')
        if len(open_year) == 8:
            open_year = open_year[:4]
        if len(start_year) == 1:
            start_year = ''
        else :
            start_year = start_year[:4]
        tmp = [title, contry, open_year, start_year, cid]
        movie_list.append(tmp)
    return movie_list

def read_movie_list_test():
    f = open('movielist/test.txt',mode='r',encoding='utf-8')
    movie_list = []
    while True:
        line = f.readline()
        if not line:
            break
        _, cid, title, contry, open_year, start_year = line.split('|')
        if len(open_year) == 8:
            open_year = open_year[:4]
        if len(start_year) == 1:
            start_year = ''
        else :
            start_year = start_year[:4]
        tmp = [title, contry, open_year, start_year, cid]
        movie_list.append(tmp)
    return movie_list

def search_title(driver, title, url, search_xpath):
    ##print('url : ',url)
    user_agent = driver.execute_script("return navigator.userAgent;")
    ##print(user_agent)
    driver.get(url) #default page에 접근
    ##print(driver)
    #html = requests.get(url).text
    ##print(html)
    elem = driver.find_element_by_xpath(search_xpath) # 메인 search name
    #elem = elem[0] #list object 상태에서는 바로 send Keys를 쓸 수 없다..
    elem.send_keys(Keys.SHIFT + Keys.END) # shift + end 키로 name value를 드레그함
    elem.send_keys(Keys.DELETE) #드레그한 value를 제거해 내가 검색하려는 타이틀만을 깔끔하게 검색하게 만듬
    elem.send_keys(title) #search block에 키워드 입력
    elem.send_keys(Keys.RETURN) #엔터 입력

def get_match(title, contry, open_year, start_year, data): #사이트 검색 결과 리스트의 영화 설명 데이터에서 검출된 스트링의 횟수를 반환
    #print('data : ',data)
    if len(data) > 85:
        return 0
    #TODO contry, year 에서 공백이 들어올 경우 처리하기
    cnt = 0
    if title in data: #타이틀명 있으면 추가
        cnt += 1
    if open_year in data or start_year in data: #개봉 또는 제작년도에 일치하는 년도 있으면 추가
        cnt += 1
    if contry in data: # 같은 나라에서 제작했으면 추가
        cnt += 1
    else:
        cnt = 0
    return cnt

def get_max(contry, open_year, start_year):
    max = 3
    if contry == '':
        max -= 1
    if open_year == '' or start_year == '':
        max -= 1
    return max

def get_url(driver, title, contry, open_year, start_year, title_xpath, check_xpath):
    max = get_max(contry, open_year, start_year)
    a = driver.find_elements_by_xpath(title_xpath) #anchor title_xpath 객체 생성
    c = driver.find_elements_by_xpath(check_xpath) # check xpath
    candidate_list = [] # 매칭 후보자 인덱스 리스트
    for i in range(len(c)):
        data = c[i].text # 설명 데이터 통째로 텍스트화
        data += a[i].text
        cnt = get_match(title, contry, open_year, start_year, data)
        elem = (i,cnt)
        candidate_list.append(elem)
    candidate_list.sort(key = lambda t : t[1], reverse=True) #검출 횟수 내림차순으로 정렬
    index = candidate_list[0][0] #정렬된 맨 앞이 가장 검출 횟수가 높음으로 우리가 찾는 영화일 확률이 높음
    match = candidate_list[0][1]
    if match < max:
        if not(len(candidate_list) == 1 and match == max-1):
            raise match_error('match cnt is not full')
    content_url = a[index].get_attribute('href')
    driver.get(content_url) #경로로 이동
    return content_url #경로 반환


def get_score(driver, score_xpath):
    try:
        s = driver.find_elements_by_xpath(score_xpath) #score xpath로 해당 elements 추출
        score = extract_score(s[0].text)
        if score == '':
            score = 'not exist'
    except:
        score = 'not exist'
    return score

def extract_score(s): # 순수하게 평점만 추출하는 함수
    score = s
    for i in range(len(s)):
        if s[i] == '\n':
            break
        if s[i] == '.':
            score = s[i-1:i+2]
    return score

def score_scaling(score, scale):
    tmp = score
    try:
        if scale == '5':
            score = float(score)*2.0
    except:
        score = tmp
    return str(score)

def get_data(driver, actor_xpath, summary_xpath):
    a = driver.find_elements_by_xpath(actor_xpath) #anchor title_xpath 객체 생성
    s = driver.find_elements_by_xpath(summary_xpath) # check xpath
    tmp = []
    for actor in a:
        tmp.append(actor.text)
    json_data = OrderedDict()
    json_data['category'] = 'movie'
    json_data['actor'] = tmp
    try:
        json_data['summary'] = s[0].text
    except:
        json_data['summary'] = 'not exist'
    return json_data

#Todo : movie list 받아서 읽기 준비, movie list 3001 ~ 끝까지 크롤링하자
#Todo : headless 있고 없고에 따라서 max movie를 받고 못받고가 정해지는데 뭐때문일까?
#Todo : 위에 cmp 체워 넣기, xpath 체워넣기, 테스트 코드 작성하기
def body(site_list, movie_list, job):
    driver = init()
    conn_string = "host = 'superson:5432' dbname ='crawling' user='superson' password='superson'"
    conn = psycopg2.connect("dbname=crawling user=superson password=superson host=superson port=5432")
    cur = conn.cursor()

    for movie in movie_list: # 영화 리스트 순회
        # title = movie['title']
        # contry = movie['contry']
        # open_year = movie['open_year']
        # start_year = movie['start_year']

        title = movie[0]
        contry = movie[1]
        open_year = movie[2]
        start_year = movie[3]
        cid = movie[4]
        # print('title : ',title)
        # print('contry : ',contry)
        # print('open_year : ',open_year)
        # print('start_year : ',start_year)
        link_list = [] #crawling 된 링크들을 담을 list
        for site in site_list: # 이 카테고리에 해당하는 사이트들 순회
            site_name = site['site_name'] # 사이트명
            scale_type = site['scale_type'] # 평점 스케일
            default_url = site['site_url'] # 사이트 기본 주소
            search_xpath = site['search_xpath'] # 사이트 검색 기능 속성명
            title_xpath = site['title_xpath'] # 기본 주소에서 타이틀로 검색한 결과 리스트 접근 title_xpath
            check_xpath = site['check_xpath'] #  year 접근
            score_xpath = site['score_xpath'] # 별점 접근 속성
            actor_xpath = site['actor_xpath'] # 배우 목록 접근
            summary_xpath = site['summary_xpath'] # 영화 내용
            if site_name == 'maxmovie':
                continue
	    #search_title(driver, title, default_url, search_xpath)
            #content_url = get_url(driver, title, contry ,open_year, start_year, title_xpath, check_xpath)
            try:
                try: #기존 타이틀 명으로 검색
                    search_title(driver, title, default_url, search_xpath)
                    content_url = get_url(driver, title, contry ,open_year, start_year, title_xpath, check_xpath)
                except: #연도를 붙여서 타이틀 검색
                    print('* except in get_url() : content_url 을 못 받아옴, title에 year 추가해서 재시도')
                    search_title(driver, title + '('+ open_year +')', default_url, search_xpath)
                    content_url = get_url(driver, title, contry ,open_year, start_year, title_xpath, check_xpath)
            except: #만약 연도를 붙여도 안나온다면
                print('* except in get_url() : get_url() 재시도 실패, '+ site_name + ' crawling은 무시')
                continue
            score = get_score(driver, score_xpath)
            score = score_scaling(score, scale_type)

            json_tmp = OrderedDict()
            json_tmp['site_name'] = site_name
            json_tmp['url'] = content_url
            json_tmp['rating'] = score
            json_tmp['data'] = get_data(driver, actor_xpath, summary_xpath)
            json_tmp['review'] = 'review'
            #TODO
            #data // category, actor, summary
            #review // if i can
            link_list.append(json_tmp)

            # print('site name : ',site_name)
            # print('url : ',content_url)
            # print('raing : ',score)
            # print('\n')
            print(site_name+' finish !')

        json_file = OrderedDict()
        json_file['doc_id'] = cid
        json_file['title'] = title
        json_file['site'] = link_list
        json_file = json.dumps(json_file,ensure_ascii=False)
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d%H%M%S')
        identify = title + '|' + contry + '|' + open_year + '|' + start_year
        # with open('data/movie/test/'+title+'_link.json', 'w', encoding='utf-8') as make_file:
        #with open('output/'+title+'_link.json', 'w', encoding='utf-8') as make_file:
        #    json.dump(json_file, make_file, ensure_ascii=False, indent="\t")
        #    print('make '+title+'_link.json file!')

        # conn_string = "host='localhost' dbname ='crawling' user='superson' password='superson'"
        # conn = psycopg2.connect(conn_string)
        # cur = conn.cursor()
        if job == 'insert':
            cur.execute("INSERT INTO rawdata_movie (doc_id, identify, date, data)  VALUES (%s, %s, %s, %s)", (cid,identify,date,json_file))
        elif job == 'test':
            cur.execute("INSERT INTO test (doc_id, identify, date, data)  VALUES (%s, %s, %s, %s)", (cid,identify,date,json_file))
        elif job == 'update':
            cur.execute("UPDATE test SET date = '"+date+"' where doc_id = '"+cid+"'") #TODO : update되는 칼럼은 date , data 두개임으로 후에 수정한다
            json_file = make_refine_json(json_file)
            cur.execute("INSERT INTO test_refine (doc_id, mid, data)  VALUES (%s, %s, %s)", (cid,"000",json_file))

         #TODO : 여기에 refine 커밋해버리는 코드도 작성해버리자 위에 인서트 부분에
        conn.commit()
    cur.close()
    conn.close()
    driver.quit()
    return 'success'

def get_update_list():
    conn = psycopg2.connect("dbname=crawling user=superson password=superson host=superson port=5432")
    cur = conn.cursor()
    now = datetime.datetime.now()
    today = now.strftime('%Y%m%d%H%M%S') #TODO : 주기정도에 따라서 - 30일? 15일 전의 날짜를 반환하도록!
    #today = '20190801145132'
    cur.execute("SELECT doc_id, identify FROM test WHERE date < '"+today+"'")
    result  = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    movie_list = []
    for data in result:
        doc_id = data[0]
        title, contry, open_year, start_year = data[1].split('|')
        tmp = [title,contry,open_year,start_year,doc_id]
        movie_list.append(tmp)
    return movie_list

def update_raw(doc_id):
    conn = psycopg2.connect("dbname=crawling user=superson password=superson host=superson port=5432")
    cur = conn.cursor()
    now = datetime.datetime.now()
    cur.execute("SELECT doc_id, identify FROM test WHERE doc_id = '"+doc_id+"'")
    result  = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    movie_list = []
    for data in result:
        doc_id = data[0]
        title, contry, open_year, start_year = data[1].split('|')
        tmp = [title,contry,open_year,start_year,doc_id]
        movie_list.append(tmp)
    site_list = read_site_list()
    body(site_list, movie_list, 'update')
    return 'update finish'

def make_refine_json(json_data):
    refine_json = OrderedDict()
    json_data = json.loads(json_data)
    site_data = json_data['site']
    list = []
    flag = True
    for site in site_data:
        tmp = OrderedDict()
        tmp['site_name'] = site['site_name']
        tmp['url'] = site['url']
        tmp['rating'] = site['rating']
        tmp['review'] = site['review']
        list.append(tmp)
        if flag:
            info = site['data']
            flag = False

    data_part = OrderedDict()
    data_part['doc_id'] = json_data['doc_id']
    data_part['title'] = json_data['title']
    tmp = OrderedDict()
    if not flag:
        data_part['category'] = info['category']
        tmp['actor'] = info['actor']
        tmp['summary'] = info['summary']
    data_part['info'] = tmp
    refine_json['data'] = data_part
    refine_json['site'] = list
    refine_json = json.dumps(refine_json,ensure_ascii=False)
    return refine_json


#
def update_refine(doc_id):
    conn = psycopg2.connect("dbname=crawling user=superson password=superson host=superson port=5432")
    cur = conn.cursor()
    now = datetime.datetime.now()
    cur.execute("SELECT data FROM test WHERE doc_id = '"+doc_id+"'")
    result  = cur.fetchall()
    conn.commit()
    for data in result:
        json_data = make_refine_json(data[0])
        cur.execute("UPDATE test_refine SET data = '"+json_data+"' where doc_id = '"+doc_id+"'")
        conn.commit()
    cur.close()
    conn.close()
    return 'insert refine finish'
#for i in range(1,4):

#site_list = read_site_list()
#movie_list = read_movie_list_test()
#body(site_list, movie_list, 'test')
#movie_list = get_update_list()
#body(site_list, movie_list, 'update')
update_raw('20113557')
print('******* finish ********')
