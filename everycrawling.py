import requests
from lxml import html
import json
import logging
import datetime
import uuid


def log_init():
    logging.basicConfig(filename='./log/test.log',format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG , datefmt='%Y-%m-%d %H:%M:%S')

#*********************************************************************

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
#print(read_site('watcha'))

def read_input(category,file_name):
    # f = open('movielist/'+category+'/'+file_name+'.txt',mode='r',encoding='utf-8')
    # input_list = []
    # while True:
    #     line = f.readline()
    #     if not line:
    #         break
    #     _, cid, title, contry, open_year, start_year = line.split('|')
    #     if len(open_year) == 8:
    #         open_year = open_year[:4]
    #     if len(start_year) == 1:
    #         start_year = ''
    #     else :
    #         start_year = start_year[:4]
    #     tmp = cid + '|' + title + '|' + contry + '|' + open_year + '|' + start_year
    #     input_list.append(tmp)
    # f.close()
    return ['000|엑시트|한국|2019|2018']
    #return input_list

#*************************************************************

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
    score = score[0].text_content()
    #score = extract_score(score)
    #score = score_scaling(score, score_scale)
    return score

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
        poster = 'not exist'
    return poster

def get_summary(tree, summary_xpath):
    summary = tree.xpath(summary_xpath)
    summary = summary[0].text_content()
    return summary

#**************************************************************
#uuid.uuid4()

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

def request_recovery(url, site):
    header = get_header()
    list = [header, url, site]
    return list

#**************************************************************

# db 속성 : uuid site id createdate data 요청 복구
def test():
    log_init()
    category = 'movie'
    site = read_site('maxmovie')
    input = read_input(category,'test')
    for n in input:
        try:
            content_url = get_url(site, n)
            raw_data = get_data(content_url, site)

            uid = uuid.uuid4()
            source_site = site['site_name']
            source_id = get_source_id(content_url)
            date = get_date()
            recovery = request_recovery(content_url, site)

        except Exception as e:
            logging.error('Exception while <'+ site['site_name']+'> searching <'+ n +'> '+ str(e))
            logging.exception('Got exception on main handler')
            continue

def make_request():
    log_init()
    category = 'movie'
    sites = read_site('all')
    input = read_input(category, 'filename')
    for movie in input:
        uid = uuid.uuid4()
        for site in sites:
            try:
                content_url = get_url(site, movie)
                raw_data = get_data(content_url, site)
                source_site = site['site_name']
                source_id = get_source_id(content_url)
                date = get_date()
                recovery = request_recovery(content_url, site)

                print('uid : ',uid)
                print('source_site : ',source_site)
                print('source_id : ',source_id)
                print('date : ',date)
                print('data : ',raw_data)
                print('recovery : ',recovery)                
                print('')

            except Exception as e:
                logging.error('Exception while <'+ site['site_name']+'> searching <'+ movie +'> '+ str(e))
                logging.exception('Got exception on main handler')
                continue

make_request()
