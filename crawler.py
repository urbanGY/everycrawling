import requests
from lxml import html
import json
from collections import OrderedDict #for make json
import datetime
from time import sleep
#*********************************************************************
# for load input data
def read_site(name):
    f = open('site/site_list.json', mode='r', encoding='utf-8')
    json_site = json.load(f)
    site_list = json_site['site_list']
    f.close()
    site = site_list
    for s in site_list:
        if name == s['site_name']:
            site = s
    return site

def read_input(category,file_name):
    f = open('input/'+category+'/'+file_name+'.txt',mode='r',encoding='utf-8')
    input_list = []
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
        tmp = cid + '|' + title + '|' + contry + '|' + open_year + '|' + start_year
        input_list.append(tmp)
    f.close()
    return input_list

#*************************************************************
# for get content_url.. get_url() func
def get_url(site_data, input_data):
    url = site_data['search_url']
    title_xpath = site_data['title_xpath']
    identify_xpath = site_data['identify_xpath']


    _, title, contry, open_year, start_year = input_data.split('|')
    url = url.replace("<TITLE>", title)
    max = get_max(contry, open_year, start_year)

    page = requests.get(url, headers = get_header())
    tree = html.fromstring(page.content)

    titles = tree.xpath(title_xpath)
    identifys = tree.xpath(identify_xpath)
    candidate_list = []

    for i in range(0,len(titles)):
        candidate_title = titles[i].text_content()
        candidate_data = identifys[i].text_content()
        match_point = get_match(input_data, candidate_title, candidate_data)
        elem = (i,match_point)
        candidate_list.append(elem)

    candidate_list.sort(key = lambda t : t[1], reverse=True)
    index = candidate_list[0][0]
    match = candidate_list[0][1]

    if match < max:
        if not(len(candidate_list) == 1 and match == max-1):
            raise match_error('match cnt is not full')
    if site_data['site_name'] == 'watcha':
        content_url = titles[index].getparent().getparent().getparent().attrib['href']
    else:
        content_url = titles[index].attrib['href']
    content_url = make_full_url(site_data, content_url)
    return content_url

def get_header():
    headers = {
    'user-agent': 'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    return headers

def get_max(contry, open_year, start_year):
    max = 3
    if contry == '':
        max -= 1
    if open_year == '' or start_year == '':
        max -= 1
    return max


def get_match(identify, candidate_title, candidate_data):
    if (len(candidate_title) + len(candidate_data)) > 90:
        return 0
    cnt = 0
    _, title, contry, open_year, start_year = identify.split('|')
    if title in candidate_title:
        cnt += 1
    if open_year in candidate_data or start_year in candidate_data: #개봉 또는 제작년도에 일치하는 년도 있으면 추가
        cnt += 1
    if contry in candidate_data:
        cnt += 1
    else:
        cnt = 0
    return cnt

def make_full_url(site, content_url):
    base_url = site['base_url']
    content_url = base_url + content_url
    return content_url

#*************************************************************
# for make raw_data.. get_data() func
def get_data(url, site_data):
    page = requests.get(url, headers = get_header())
    tree = html.fromstring(page.content)

    score_xpath = site_data['score_xpath']
    score_scale = site_data['scale_type']
    score = get_score(tree, score_xpath, score_scale)

    actor_xpath = site_data['actor_xpath']
    actor = get_actor(tree, actor_xpath)

    poster_xpath = site_data['poster_xpath']
    poster = get_poster(tree, poster_xpath)

    summary_xpath = site_data['summary_xpath']
    summary = get_summary(tree, summary_xpath)

    raw_data = score + '|'
    raw_data += actor + '|'
    raw_data += poster + '|'
    raw_data += summary
    return raw_data

def get_score(tree, score_xpath, score_scale):
    score = tree.xpath(score_xpath)
    try:
        score = score[0].text_content()
    except:
        score = 'score not exist'
    return score

def get_actor(tree, actor_xpath):
    actor = tree.xpath(actor_xpath)
    actor = extract_actor(actor)
    return actor

def extract_actor(a):
    actor_list = []
    for actor in a:
        actor_list.append(actor.text_content())
    return str(actor_list)

def get_poster(tree, poster_xpath):
    poster = tree.xpath(poster_xpath)
    try:
        poster = poster[0].attrib['src']
    except:
        poster = 'poster not exist'
    return poster

def get_summary(tree, summary_xpath):
    summary = tree.xpath(summary_xpath)
    summary = summary[0].text_content()
    return summary

#**************************************************************
#for raw_data attribute

def get_source_id(url):
    for i in range(len(url)-1,0,-1):
        if url[i] == '/' or url[i] == '=':
            break
    source_id = url[i+1:len(url)]
    return source_id

def get_date():
    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d%H%M')
    return date

def request_recovery(movie, url, site):
    header = get_header()
    list = [movie, header, url, site]
    return str(list)

#**************************************************************
# for make json
def make_json(list):
    for tup in list:
        source_site = tup[0]
        rawdata = tup[1]
        score, actor_list, poster, summary = rawdata.split('|')
    #json 폼으로 만들기!!
    {
        "data":{
            "doc_id":"20113557",
            "title":"범죄와의 전쟁: 나쁜놈들 전성시대",
            "category":"movie",
            "info":{
                "poster_url":"https://dhgywazgeek0d.cloudfront.net/watcha/image/upload/c_fill,h_400,q_80,w_280/v1466077889/oybh6wd5sokcttwcaywt.jpg",
                "actor":[
                    "윤종빈",
                    "최민식",
                    "하정우",
                    "조진웅",
                    "곽도원",
                    "김성 균",
                    "마동석",
                    "김혜은",
                    "송영창"
                ],
            "summary":"1982년 부산. 해고될 위기에 처한 비리 세관원 최익현(최민식)은 순찰 중 적발한 히로뽕을 일본으로 밀수출, 마지막으로 한 탕 하기 위해 부산 최대 조직의 젊은 보스 최형배(하정우)와 손을 잡는다. 익현은 탁월한 임기응변과 특유의 친화력으로…"
            }
        },
        "site":[
            {
                "site_name":"watcha",
                "url":"https://watcha.com/ko-KR/contents/mWv1lb5",
                "rating":"8.0",
                "review":"review"
            },
            {
                "site_name":"naver_movie",
                "url":"https://movie.naver.com/movie/bi/mi/basic.nhn?code=82540",
                "rating":"8.6",
                "review":"review"
            },
            {
                "site_name":"daum_movie",
                "url":"http://movie.daum.net/moviedb/mai n?movieId=63114",
                "rating":"8.3",
                "review":"review"
            }
        ]
    }
    return json_form

def extract_score(s):
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

#**************************************************************
# db 속성 : uuid site id createdate data 요청 복구
def test():
    import logging
    logging.basicConfig(filename='./log/test.log',format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG , datefmt='%Y-%m-%d %H:%M:%S')
    category = 'movie'
    sites = read_site('all')
    # input = ['000|엑시트|한국|2019|2018']
    # 20182407|우리의 소원|한국||2018 #매치 에러 이거 해결
    input = ['20192601|작은 방안의 소녀|한국||2018'] #스코어 에러
    for movie in input:
        sleep(1)
        for site in sites:
            try:
                content_url = get_url(site, movie)
                print('url : ',content_url)
                raw_data = get_data(content_url, site)
                source_site = site['site_name']
                source_id = get_source_id(content_url)
                date = get_date()
                recovery = request_recovery(movie, content_url, site)
                print('source_site : ',source_site)
                print('source_id : ',source_id)
                print('date : ',date)
                print('data : ',raw_data)
                print('recovery : ',recovery)
                print('')
            except Exception as e:
                logging.error('Exception while <'+ site['site_name']+'> searching <'+ movie +'> '+ str(e))
                logging.exception('Got exception')
                logging.error('**********************************')
                continue
#test()
