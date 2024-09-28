from django.urls import path
from .views import Linewebhook

urlpatterns=[
    path("callback/",Linewebhook.as_view()),
]