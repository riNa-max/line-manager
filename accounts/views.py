from django.contrib.auth.views import LoginView
from .forms import LoginForm

from django.urls import reverse_lazy
from django.views.generic import ListView
from .models import Account
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LogoutView

class AccountLoginView(LoginView):
    template_name='login.html'
    form_class=LoginForm

    def get_success_url(self):
        return reverse_lazy('dashboard')
    
@method_decorator(login_required(login_url='/'), name='dispatch')
class DashboardView(ListView):
    template_name='dashboard.html'
    model=Account
    
    # context_object_name='users'

class LogoutView(LogoutView):
    template_name='logout.html'
