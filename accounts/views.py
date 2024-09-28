from django.contrib.auth.views import LoginView
from .forms import LoginForm

from django.urls import reverse_lazy
from django.views.generic import ListView
from .models import Account
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LogoutView

from manager.models import LineAccount,LineMessage

from django.db.models import Q
from django.db.models import Max
from datetime import timedelta
from django.utils import timezone

class AccountLoginView(LoginView):
    template_name='login.html'
    form_class=LoginForm

    def get_success_url(self):
        return reverse_lazy('dashboard')
    
@method_decorator(login_required(login_url='/'), name='dispatch')
class DashboardView(ListView):
    template_name='dashboard.html'
    model=Account

    def get_context_data(self, **kwargs):
        # 団体名の表示
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user

        # 並び替えフィルター
        sort_option = self.request.GET.get('sort', 'name-asc')
        if sort_option == 'name-asc':
            line_users = LineAccount.objects.all().order_by('display_name')
        elif sort_option == 'latest-date':
            line_users = LineAccount.objects.annotate(last_sent=Max('linemessage__last_sent_date')).order_by('-last_sent')
        context['sort_option'] = sort_option

        # 検索バー
        query = self.request.GET.get('q','')
        if query:
            line_users = LineAccount.objects.filter(display_name__icontains=query)
        else:
            line_users = LineAccount.objects.all()
        context['search_query'] = query

        # 絞り込みフィルター
        filter_option = self.request.GET.get('filter', None)
        three_months_ago = timezone.now() - timedelta(days=90)

        users_with_last_message = []
        if filter_option == 'over_three_months':
            for user in line_users:
                last_message = LineMessage.objects.filter(user=user).order_by('-last_sent_date').first()
                if last_message and last_message.last_sent_date < three_months_ago:
                    users_with_last_message.append({
                        'user': user.display_name,
                        'last_sent_date': last_message.last_sent_date,
                        'created_at': user.created_at
                    })
        else:
            # ユーザー名、最終送信日時、登録日の取得（絞り込みがない場合）
            for user in line_users:
                last_message = LineMessage.objects.filter(user=user).order_by('-last_sent_date').first()
                users_with_last_message.append({
                    'user': user.display_name,
                    'last_sent_date': last_message.last_sent_date if last_message else None,  # 最終送信日がなければNone
                    'created_at': user.created_at
                })
        context['users_with_last_message'] = users_with_last_message
        context['filter_option'] = filter_option

        return context

class LogoutView(LogoutView):
    template_name='logout.html'
