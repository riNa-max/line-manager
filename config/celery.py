from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Django settings fileへのパスを設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Celeryアプリケーションを作成
app = Celery('config')

# Djangoの設定をCeleryに読み込ませる
app.config_from_object('django.conf:settings', namespace='CELERY')

# Djangoアプリからタスクモジュールをロード
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))