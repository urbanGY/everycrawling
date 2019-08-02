from everycrawling.celery import app
from . import link_crawling

@app.task
def say_hello():
    print('helllo !')

@app.task
def insert_raw_data():
    movie_list = link_crawling.read_movie_list_test()
    site_list = link_crawling.read_site_list()
    result = link_crawling.body(site_list, movie_list, 'insert')
    print(result)

@app.task
def update_raw_data_schedule():
    movie_list = link_crawling.get_update_list()
    site_list = link_crawling.read_site_list()
    result = link_crawling.body(site_list, movie_list, 'update')
    print(result)

@app.task
def update_raw_data(doc_id):
    link_crawling.update_raw(doc_id)
