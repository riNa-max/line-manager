from django.urls import path
from .views import AccountLoginView

urlpatterns=[
    path("",AccountLoginView.as_view(),name="login"),
]