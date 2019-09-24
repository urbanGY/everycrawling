import requests
from lxml import html
import json
from collections import OrderedDict #for make json
import datetime
from time import sleep
import re # regular expression
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
def get_raw_data(url):
    page = requests.get(url, headers = get_header()).text
    return page

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

def request_recovery(category, identify, url, site):
    header = get_header()
    list = [category, identify, header, url, site]
    return str(list)

#**************************************************************
# for make json
def make_json(uuid, list):
    import ast
    poster = ''
    max_summary = ''
    max_actor = [[],[]]
    title = ''

    site_info_list = []
    for tup in list:
        source_site = tup[0] #naver, daum..
        rawdata = tup[1] #html
        recovery = tup[2]
        recovery = ast.literal_eval(recovery) #string form list ro list

        category = recovery[0]
        identify = recovery[1]
        url = recovery[3]
        site = recovery[4]

        score, actor_list, poster_url, summary = get_data(rawdata, site)
        _, title, contry, open_year, start_year = identify.split('|')

        if source_site == 'naver_movie':
            poster = poster_url

        max_summary = get_max_summary(summary, max_summary)
        max_actor = get_max_actor(actor_list, max_actor)

        tmp = OrderedDict()
        tmp['site_name'] = source_site
        tmp['url'] = url
        tmp['rating'] = score
        site_info_list.append(tmp)

    info_part = OrderedDict() #poster, actor, summary
    info_part['poster_url'] = poster
    info_part['director'] = max_actor[0]
    info_part['actor'] = max_actor[1]
    info_part['summary'] = max_summary

    data_part = OrderedDict()
    data_part['uuid'] = uuid
    data_part['category'] = category
    data_part['title'] = title
    data_part['info'] = info_part

    json_form = OrderedDict()
    json_form['data'] = data_part
    json_form['site'] = site_info_list
    j = json.dumps(json_form,ensure_ascii=False)
    return json.loads(j)

def get_max_summary(summary, max):
    if len(summary) > len(max):
        max = summary
    return max

def get_max_actor(actor, max):
    if len(actor[1]) > len(max[1]):
        max = actor
    return max

def get_data(page, site_data):
    tree = html.fromstring(page)

    score_xpath = site_data['score_xpath']
    score_scale = site_data['scale_type']
    score = get_score(tree, score_xpath)
    score = extract_score(score)
    score = score_scaling(score, score_scale)

    actor_xpath = site_data['actor_xpath']
    actor = get_actor(tree, actor_xpath)

    poster_xpath = site_data['poster_xpath']
    poster = get_poster(tree, poster_xpath)

    summary_xpath = site_data['summary_xpath']
    summary = get_summary(tree, summary_xpath)
    summary = remove_blank(summary)

    return score, actor, poster, summary

def get_score(tree, score_xpath):
    score = tree.xpath(score_xpath)
    try:
        score = score[0].text_content()
    except:
        score = '0.0'

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

#감독 파싱하기
def get_actor(tree, actor_xpath):
    actor = tree.xpath(actor_xpath)
    list = extract_actor(actor)
    if len(list) > 0:
        cnt = get_director_cnt(actor)
        director_list = list[0:cnt]
        actor_list = list[cnt:]
        list = [director_list, actor_list]
    else :
        list = [[],[]]
    return list

def extract_actor(a):
    actor_list = []
    for actor in a:
        actor_list.append(actor.text_content())
    if len(actor_list) > 0 and (actor_list[0] == '왓챠플레이' or actor_list[0] == 'TVING'):
        actor_list = actor_list[1:len(actor_list)]
    return actor_list

def get_director_cnt(a):
    director_cnt = 0
    node = a[len(a)-1]
    while True:
        if 'ul' in str(node):
            all_info = node.text_content()
            director_cnt = all_info.count('감독')
            break
        node = node.getparent()
    return director_cnt

def get_poster(tree, poster_xpath):
    poster = tree.xpath(poster_xpath)
    try:
        poster = poster[0].attrib['src']
    except:
        poster = 'poster not exist'
    return poster

def get_summary(tree, summary_xpath):
    summary = tree.xpath(summary_xpath)
    try:
        summary = summary[0].text_content()
    except:
        summary = 'summary not exist'
    return summary

def remove_blank(s): # 9 10 32 앞 뒤에 있는 과도한 공백들 제거
    for front in range(0,len(s)):
        if not (ord(s[front]) is 9 or ord(s[front]) is 10 or ord(s[front]) is 32):
            break

    for tail in range(len(s)-1,0,-1):
        if not (ord(s[tail]) is 9 or ord(s[tail]) is 10 or ord(s[tail]) is 32):
            break

    s = s[front:tail+1]
    return s
#**************************************************************
# db 속성 : uuid site id createdate data 요청 복구
def test():
    import logging
    logging.basicConfig(filename='./log/test.log',format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG , datefmt='%Y-%m-%d %H:%M:%S')
    category = 'movie'
    sites = read_site('all')
    #input = ['000|엑시트|한국|2019|2018']
    input = ['000|매트릭스 3 - 레볼루션|미국|2003|2003']
    # 20182407|우리의 소원|한국||2018 #매치 에러 이거 해결 **
    # input = ['20192601|작은 방안의 소녀|한국||2018'] #스코어 에러 **
    for movie in input:
        sleep(1)
        for site in sites:
            try:
                content_url = get_url(site, movie)
                print('url : ',content_url)
                raw_data = get_raw_data(content_url)
                data = get_data(raw_data, site)
                source_site = site['site_name']
                source_id = get_source_id(content_url)
                date = get_date()
                recovery = request_recovery(category, movie, content_url, site)

                # print('source_site : ',source_site)
                # print('source_id : ',source_id)
                # print('date : ',date)
                # print('raw data : ',raw_data)
                # print('data : ',data)
                # print('recovery : ',recovery)
                # print('')
            except Exception as e:
                logging.error('Exception while <'+ site['site_name']+'> searching <'+ movie +'> '+ str(e))
                logging.exception('Got exception')
                logging.error('**********************************')
                continue

#test()
def get_html_test():
    naver_url = 'https://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code=<SOURCE>&type=after&page=1'
    total_xpath = '/html/body/div/div/div[4]/strong/em'
    review_xpath = '/html/body/div/div/div[6]/ul/li[not(@*)]'

    category = 'movie'
    site = read_site('naver_movie')
    input = ['000|엑시트|한국|2019|2018']
    for movie in input:
        content_url = get_url(site, movie)
        source_id = get_source_id(content_url)
        url = naver_url.replace("<SOURCE>",source_id)
        page = requests.get(url, headers = get_header())
        tree = html.fromstring(page.content)
        total = tree.xpath(total_xpath)
        for i in range(1,5):#int(total/10) + 1
            url = url.replace('page=1','page='+str(i))
            page = requests.get(url, headers = get_header())
            tree = html.fromstring(page.content)
            r = tree.xpath(review_xpath)
            for li in r:
                review = li.xpath('div/p') # 리뷰
                score = li.xpath('div/em')
                strong = li.xpath('div/strong/span')
                print(review[0].text_content())
                print(score[0].text_content())
                print(strong[0].text_content())

def get_naver_review(source_id):
    naver_url = 'https://movie.naver.com/movie/bi/mi/review.nhn?code=<SOURCE_ID>&page=<INDEX>'
    detail_url = 'https://movie.naver.com/movie/bi/mi/reviewread.nhn?nid=<NID>&code=<SOURCE_ID>&order=#tab'
    naver_url = naver_url.replace('<SOURCE_ID>',source_id)
    detail_url = detail_url.replace('<SOURCE_ID>',source_id)

    total_xpath = '//*[@id="reviewTab"]/div/div/div[2]/span/em/text()'
    li_xpath = '//*[@id="reviewTab"]/div/div/ul/li[not(@*)]'

    total_url = naver_url.replace('<INDEX>','1')
    page = requests.get(total_url,headers = get_header())
    tree = html.fromstring(page.content)
    total = tree.xpath(total_xpath)
    try:
        total = total[0]
    except:
        total = '0'

    review_list = []
    for index in range(1,int(total)//10+2):
        if index % 2 == 0:
            sleep(1)
        url = naver_url.replace('<INDEX>',str(index))
        page = requests.get(url,headers = get_header())
        tree = html.fromstring(page.content)
        li_elem = tree.xpath(li_xpath)
        for li in li_elem:
            anchor = li.xpath('a')
            a = anchor[0].attrib['onclick']
            nid = re.findall("\d+", a)
            nid = str(nid[0])
            d_url = detail_url.replace('<NID>',nid)
            page = requests.get(d_url,headers = get_header())
            tree = html.fromstring(page.content)

            user_name = tree.xpath('//*[@id="content"]/div[1]/div[4]/div[1]/div[3]/ul/li[not(@*)]/a/em')
            review = tree.xpath('//*[@id="content"]/div[1]/div[4]/div[1]/div[4]')
            date = tree.xpath('//*[@id="content"]/div[1]/div[4]/div[1]/div[2]/span')
            rating = tree.xpath('//*[@id="content"]/div[1]/div[4]/div[1]/div[2]/div/em')
            user_name = user_name[len(user_name)-1].text_content()
            review = review[0].text_content()
            review = remove_blank(review)
            date = date[0].text_content()
            try:
                rating = rating[0].text_content()
            except:
                rating = 'none'

            tmp = [user_name, review, date, rating]
            review_list.append(tmp)
    return review_list
            # print('user : ',user_name[len(user_name)-1].text_content())
            # print('review : ',review[0].text_content())
            # print('date : ',date[0].text_content())
            # try:
            #     print('rating : ',rating[0].text_content())
            # except:
            #     print('rating : none')
            # print('************************************************************\n')




def ajax_header(refer):
    headers = {'accept': 'application/vnd.frograms+json;version=20',
    'Origin': 'https://watcha.com',
    'Referer': refer,
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'x-watcha-client': 'watcha-WebApp',
    'x-watcha-client-language': 'ko',
    'x-watcha-client-region': 'KR',
    'x-watcha-client-version': '1.0.0'}
    return headers

def get_watcha_review(source_id):
    # refer = 'https://watcha.com/ko-KR/contents/mdErj22/comments' #엑시트 댓글 담고있는 주소
    # ajax_url = 'https://api.watcha.com/api/contents/mdErj22/comments?default_version=20&filter=all&order=popular&page=<INDEX>&size=3&vendor_string=frogram'

    refer = 'https://watcha.com/ko-KR/contents/<SOURCE_ID>/comments'
    ajax_url = 'https://api.watcha.com/api/contents/<SOURCE_ID>/comments?default_version=20&filter=all&order=popular&page=<INDEX>&size=3&vendor_string=frograms'

    refer = refer.replace('<SOURCE_ID>',source_id)
    ajax_url = ajax_url.replace('<SOURCE_ID>',source_id)

    index = 1
    review_list = []
    while True:
        if index % 4 == 0:
            sleep(1)
        #sleep need??
        url = ajax_url.replace("<INDEX>",str(index))
        index += 1;
        req = requests.get(url, headers = ajax_header(refer)).text
        json_data = json.loads(req)
        result_part = json_data['result']
        next = result_part['next_uri']
        if next == None:
            break
        result_list = result_part['result']
        for result in  result_list:
            user = result['user']['name']
            user_name = result['user']['name']
            review = result['text']
            date = result['created_at']
            rating = result['user_content_action']['rating']
            tmp = [user_name, review, date, rating]
            review_list.append(tmp)
    return review_list
            # print('user : ',user_name)
            # print('review : ',review)
            # print('date : ',date)
            # print('rating : ',rating)
            # print('************************************************************\n')
            #여기서 next uri가 null 인지 검사해서 정지하는 코드 삽입
            #result_part['next_uri'] = null


def get_daum_review(source_id):
    daum_url = 'https://movie.daum.net/moviedb/grade?movieId=<SOURCE_ID>&type=netizen&page=<INDEX>'
    daum_url = daum_url.replace('<SOURCE_ID>',source_id)

    total_xpath = '//*[@id="mArticle"]/div[2]/div[2]/div[1]/div[1]/h4/span[1]'
    li_xpath = '//*[@id="mArticle"]/div[2]/div[2]/div[1]/ul/li[@*]'

    total_url = daum_url.replace('<INDEX>','1')
    page = requests.get(total_url,headers = get_header())
    tree = html.fromstring(page.content)
    total_elem = tree.xpath(total_xpath)
    try:
        total = total_elem[0].text_content()
        total = total.replace('(','')
        total = total.replace(')','')
        total = total.replace(',','')
    except:
        total = '0'
    review_list = []
    for index in range(1,int(total)//10+2):
        if index % 4 == 0:
            sleep(1)
        url = daum_url.replace('<INDEX>',str(index))
        page = requests.get(url,headers = get_header())
        tree = html.fromstring(page.content)
        li_elem = tree.xpath(li_xpath)
        for li in li_elem:
            user_name = li.xpath('div/a[1]/em')
            review = li.xpath('div/p')
            date = li.xpath('div/div[2]/span[1]')
            rating = li.xpath('div/div[1]/em')
            user_name = user_name[0].text_content()
            review = review[0].text_content()
            review = remove_blank(review)
            date = date[0].text_content()
            date = remove_blank(date)
            try:
                rating = rating[0].text_content()
            except:
                rating = 'none'
            tmp = [user_name, review, date, rating]
            review_list.append(tmp)
    return review_list


def get_maxmovie_review(source_id):
    max_url = 'http://www.maxmovie.com/Movie/<SOURCE_ID>/talk?size=10&no=<INDEX>'
    max_url = max_url.replace('<SOURCE_ID>',source_id)

    total_xpath = '//*[@id="content"]/div[1]/div[2]/div[3]/div[2]/div/ul/li[1]/a/em'
    li_xpath = '//*[@id="content"]/div[1]/div[2]/div[3]/div[2]/ul/li[@*]'


    total_url = max_url.replace('<INDEX>','1')
    page = requests.get(total_url,headers = get_header())
    tree = html.fromstring(page.content)
    total_elem = tree.xpath(total_xpath)
    try:
        total = total_elem[0].text_content()
    except:
        total = '0'

    review_list = []
    for index in range(1,int(total)//10+2):
        if index % 4 == 0:
            sleep(1)
        url = max_url.replace('<INDEX>',str(index))
        page = requests.get(url,headers = get_header())
        tree = html.fromstring(page.content)
        li_elem = tree.xpath(li_xpath)
        # print(li_elem)
        for li in li_elem:
            user_name = li.xpath('div/div/p[1]/text()')
            review = li.xpath('div/div/p[2]')
            date = li.xpath('div/div/p[1]/span')
            rating = li.xpath('div/p/span[2]')

            user_name = remove_blank(user_name[0])
            review = review[0].text_content()
            review = remove_blank(review)
            date = date[0].text_content()
            try:
                rating = rating[0].text_content()
            except:
                rating = 'none'
            tmp = [user_name, review, date, rating]
            review_list.append(tmp)
    return review_list

            # print('user : ',user_name)
            # print('review : ',review[0].text_content())
            # print('date : ',date[0].text_content())
            # print('rating : ',rating[0].text_content())
            # print('************************************************************\n')
#TODO : 중복 pk가 중복되서 안들어 가는 경우가 있다;

#max movie M000106709
#daum 121137
#naver 174903
#test_maxmovie('M000106709')
# test_daum('121137')
# test_naver('174903')
# r = get_maxmovie_review('M000109052')
# r = get_watcha_review('m5m1wp7')
# r = get_daum_review('113920')
# r = get_naver_review('171911')91606
# r = get_naver_review('91606')
# for l in r:
#     print(l)
#watcha byavDOx 이건 10개짜리
# test_watcha('byavDOx')
