from django.urls import path
from .views import DashboardView,AccountLoginView,LogoutView

urlpatterns=[
    path("",AccountLoginView.as_view(),name="login"),
    path("dashboard/",DashboardView.as_view(),name="dashboard"),
    path("logout/",LogoutView.as_view(), name='logout')
]