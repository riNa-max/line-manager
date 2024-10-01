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

from linebot import LineBotApi
from linebot.models import TextSendMessage
from config.settings import LINE_ACCESS_TOKEN,LINE_USER_ID

class AccountLoginView(LoginView):
    template_name='login.html'
    form_class=LoginForm

    def get_success_url(self):
        return reverse_lazy('dashboard')
    
line_bot_api=LineBotApi(LINE_ACCESS_TOKEN)

# 管理者に通知する関数
def notify_inactive_users_to_admin(inactive_users):
    admin_line_id = LINE_USER_ID
    if inactive_users:
        user_names = [user['user'] for user in inactive_users]
        message = f"以下のユーザーは3か月以上メッセージを送信していません:\n" + "\n".join(user_names)
    else:
        message = "3か月以上メッセージを送っていないユーザーはいません。"

    line_bot_api.push_message(admin_line_id, TextSendMessage(text=message))

# プロフィール名の更新を反映
def update_all_line_profiles():
    accounts = LineAccount.objects.all()  # すべてのLINEアカウントを取得
    updated_accounts = []

    for account in accounts:
        try:
            profile = line_bot_api.get_profile(account.user_id)
            display_name = profile.display_name

            if account.display_name != display_name:
                account.display_name = display_name
                account.save()
                updated_accounts.append(account.display_name) 

        except LineAccount.DoesNotExist:
            continue
        except Exception as e:
            print(f"Error updating profile for user_id {account.user_id}: {e}")
    
    return updated_accounts

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
        inactive_users = [] 

        if filter_option == 'over_three_months':
            for user in line_users:
                last_message = LineMessage.objects.filter(user=user).order_by('-last_sent_date').first()
                if last_message and last_message.last_sent_date < three_months_ago:
                    user_data ={
                        'user': user.display_name,
                        'last_sent_date': last_message.last_sent_date,
                        'created_at': user.created_at
                    }
                    users_with_last_message.append(user_data)
                    inactive_users.append(user_data)
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

        # 管理者に通知する（該当ユーザーがいる場合）
        if filter_option == 'over_three_months':
            notify_inactive_users_to_admin(inactive_users)

        # プロフィール名を更新する関数を呼び出し
        updated_accounts = update_all_line_profiles()
        context['updated_accounts'] = updated_accounts

        return context

class LogoutView(LogoutView):
    template_name='logout.html'
