from everycrawling.celery import app
from . import link_crawling

@app.task
def say_hello():
    print('helllo !')

@app.task
def update_data():
    movie_list = link_crawling.read_movie_list_test()
    site_list = link_crawling.read_site_list()
    result = link_crawling.body(site_list, movie_list)
    print(result)
