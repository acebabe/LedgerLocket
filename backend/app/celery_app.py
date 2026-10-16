from celery import Celery
from flask import Flask

celery = Celery(__name__)

def init_celery(app: Flask):
    celery.conf.broker_url = app.config.get('CELERY_BROKER_URL')
    celery.conf.result_backend = app.config.get('CELERY_RESULT_BACKEND')
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
