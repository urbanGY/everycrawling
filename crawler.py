# -*- coding: utf-8 -*-
import requests
import random
import json
import datetime
from time import sleep
# *********************************************************************
# for load input data



def read_site(category, name):
    path = 'site/'+category+'_site_list.json'
    f = open(path, mode='r', encoding='utf-8')
    json_site = json.load(f)
    site_list = json_site['site_list']
    f.close()
    site = site_list
    for s in site_list:
        if name == s['site_name']:
            site = s
    return site

def read_input(category, start, end):
    input_list = []
    if category == 'movie':
        from category.movie.movie_module import movie_input_api
        for i in range(start,end+1):
            tmp = movie_input_api(i)
            for elem in tmp:
                input_list.append(elem)
    elif category == 'restaurant':
        from category.restaurant.restaurant_module import restaurant_input_api
        for i in range(start,end+1):
            tmp = restaurant_input_api(i)
        input_list = tmp
    return input_list

# @dataclass
# class WatchaCommentPolicy:
#     def delay(self):
#         return 1.3 + random.random()
#
#     def header(self):
#         return {
#             ...
#         }
#
#
#
# class Crawler:
#     def __init__(self, policy):
#         self.policy = policy
#         self.session = requests.Session()
#
#     def request(self, url, method='GET', params={}):
#         header = self.policy.header()
#         resp = self.session.request(url, method=method, params=params)
#         sleep(self.policy.delay())
#         return resp
#
#
# class WatchaCrawler(Crawler):
#     def request(self, url, source_id, method='GET', params={}):
#         header = self.policy.header(source_id)
#         resp = self.session.request(url, method=method, params=params)
#         sleep(self.policy.delay())
#         return resp()
#
#
# watchar_crawler = Crawler(WatchaCommentPolicy)
# korbis_crawler = Crawler(KorbisPolicy)


# *************************************************************
# for get content_url.. get_url() func
def get_url(category, site_data, input_data):
    if category == 'movie':
        from category.movie.movie_module import get_movie_url
        url = get_movie_url(site_data, input_data)
    elif category == 'restaurant':
        from category.restaurant.restaurant_module import get_restaurant_url
        url = get_restaurant_url(site_data, input_data)
    return url

# *************************************************************
# for make raw_data.. get_data() func

def get_raw_data(url):
    page = requests.get(url, headers=get_header()).text
    return page

def get_header():
    headers = {
        'user-agent': 'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    return headers
#test code
# site = read_site('movie','naver_movie')
# input = read_input('movie',1,1)
# url = get_url('movie',site,input[0])
# print(get_raw_data(url))


# **************************************************************
# for raw_data attribute


def get_source_id(url):
    for i in range(len(url)-1, 0, -1):
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

# **************************************************************
# for make json

def make_json(category, uuid, list):
    if category == 'movie':
        from category.movie.movie_module import make_movie_json
        json_data = make_movie_json(uuid,list)
    elif category == 'restaurant':
        from category.restaurant.restaurant_module import make_restaurant_json
        json_data = make_restaurant_json(uuid,list)
    return json_data

# **************************************************************
# for review request

def get_review(category, source_site, source_id):
    review_list = []
    if category == 'movie':
        from category.movie import movie_review
        if source_site == 'naver_movie':
            review_list = movie_review.get_naver_review(source_id)
        elif source_site == 'watcha':
            review_list = movie_review.get_watcha_review(source_id)
        elif source_site == 'daum_movie':
            review_list = movie_review.get_daum_review(source_id)
        elif source_site == 'maxmovie':
            review_list = movie_review.get_maxmovie_review(source_id)
    elif category == 'restaurant':
        if source_site == 'dining_code':
            review_list = restaurant_review.get_dining_review(source_id)
    return review_list



def test():
    import logging
    logging.basicConfig(filename='./log/test.log', format='%(asctime)s %(levelname)-8s %(message)s',level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
    category = 'restaurant'
    sites = read_site(category, 'all')
    input = [['1','1','1','서울특별시 종로구 명륜4가 149-0번지','','박석고개'], ['1','1','1','제주특별자치도 제주시 도두일동 2587-4번지','제주특별자치도 제주시 도두항길 16','도두해녀의집','1','1'], ['1','1','1','제주특별자치도 서귀포시 안덕면 창천리 160-4.7번지','제주특별자치도 서귀포시 안덕면 창천중앙로24번길 16','춘심이네','1','1']]
    for elem in input:
        sleep(1)
        for site in sites:
            source_site = site['site_name']
            print('source_site : ',source_site)
            content_url = get_url(category, site, elem)
            if content_url == None:
                print('url : None')
                print('***************\n\n')
                continue
            raw_data = get_raw_data(content_url)
            # data = get_data(raw_data, site)

            source_id = get_source_id(content_url)
            date = get_date()
            recovery = request_recovery(category, elem, content_url, site)


            print('url : ', content_url)
            print(len(raw_data))
            print('source_id : ',source_id)
            print('date : ',date)
            # print('raw data : ',raw_data)
            # print('data : ',data)
            print('recovery : ',recovery)
            print('***************\n\n')
        break

# test()

    # print('user : ',user_name)
    # print('review : ',review[0].text_content())
    # print('date : ',date[0].text_content())
    # print('rating : ',rating[0].text_content())
    # print('************************************************************\n')


# if __name__ == '__main__':
#     # TODO : 중복 pk가 중복되서 안들어 가는 경우가 있다;
#     # max movie M000106709
#     # daum 121137
#     # naver 174903
#     # test_maxmovie('M000106709')
#     # test_daum('121137')
#     # test_naver('174903')
#     # r = get_maxmovie_review('M000109052')
#     r = get_watcha_review('m5m1wp7')
#     # r = get_daum_review('113920')
#     # r = get_naver_review('171911')91606
#     # r = get_naver_review('91606')
#     print(len(r))
#     for l in r:
#         print(l)
    # watcha byavDOx 이건 10개짜리
    # test_watcha('byavDOx')
