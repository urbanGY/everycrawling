import os
from celery import Celery
from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# `celery` 프로그램을 작동시키기 위한 기본 장고 세팅 값을 정한다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'everycrawling.settings')

app = Celery('everycrawling')

# namespace='CELERY'는 모든 셀러리 관련 구성 키를 의미한다. 반드시 CELERY라는 접두사로 시작해야 한다.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    CELERY_TIMEZONE='Asia/Seoul',
    CELERY_ENABLE_UTC=False,
    CELERYBEAT_SCHEDULE = {
        'say_hello-every-minutes': {
            'task': 'everycrawling.task.say_hello',
            'schedule': crontab(hour='*', minute='*'),
            'args': ()
        },
        'test_crawling_schedule': {
            'task': 'everycrawling.task.update_data',
            'schedule': crontab(hour='*', minute='*'),
            'args': ()
        },
    }
)
# 장고 app config에 등록된 모든 taks 모듈을 불러온다.
app.autodiscover_tasks()
