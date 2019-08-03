from celery import Celery
from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

#app = Celery('everycrawling')
app = Celery('setting', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
app.conf.update(
    CELERY_TIMEZONE='Asia/Seoul',
    CELERY_ENABLE_UTC=False,
    CELERYBEAT_SCHEDULE = {
        'say_hello-every-minutes': {
            'task': 'task.say_hello',
            'schedule': crontab(hour='*', minute='*'),
            'args': ()
        },
        'test_crawling_schedule': {
            'task': 'task.update_data',
            'schedule': crontab(hour='*', minute='*'),
            'args': ()
        },
    }
)
