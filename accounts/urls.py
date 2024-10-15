from django.urls import path
from .views import DashboardView,AccountLoginView,LogoutView,edit_line_username, update_line_username,settings_view

urlpatterns=[
    path("",AccountLoginView.as_view(),name="login"),
    path("dashboard/",DashboardView.as_view(),name="dashboard"),
    path("logout/",LogoutView.as_view(), name='logout'),
    path('edit-line-username/<str:user_id>/', edit_line_username, name='edit_line_username'),
    path('update-line-username/<str:user_id>/', update_line_username, name='update_line_username'),
    path('settings/', settings_view, name='settings'),
]