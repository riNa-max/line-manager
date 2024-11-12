from django.urls import path
from .views import Linewebhook

urlpatterns=[
    path("callback/<str:channel_id>/",Linewebhook.as_view()),
]