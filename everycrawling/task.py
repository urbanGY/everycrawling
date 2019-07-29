from everycrawling.celery import app
from . import link_crawling

@app.task
def say_hello():
    print('helllo !')
