from celery import Celery
from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

#app = Celery('everycrawling')
app = Celery('celery_setting', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
app.conf.update(
    #CELERY_TIMEZONE='Asia/Seoul',
    CELERY_ENABLE_UTC=False,
    CELERYBEAT_SCHEDULE = {
        'hello': {
            'task': 'task.hello',
            'schedule': crontab(hour='*', minute='*'),
            'args': ()
        },
        'rawdata_crawling': {
            'task': 'task.rawdata_crawling_schedule',
            'schedule': crontab(hour='*', minute='*'),
            'args': ()
        },
        'add_new_movie': {
            'task': 'task.add_new_movie_schedule',
            'schedule': crontab(hour='*', minute='*'),
            'args': ()
        },
    }
)
