from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import LoginForm

# Create your views here.

class AccountLoginView(LoginView):
    template_name='login.html'
    form_class=LoginForm