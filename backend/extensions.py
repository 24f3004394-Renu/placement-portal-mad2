from flask_caching import Cache
from celery import Celery

cache = Cache()
celery = Celery(__name__)