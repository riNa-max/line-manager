from django.contrib.auth.views import LoginView
from .forms import LoginForm

from django.urls import reverse_lazy
from django.views.generic import View
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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

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

# 編集画面を表示するビュー
def edit_line_username(request, user_id):
    user = get_object_or_404(LineAccount, user_id=user_id)
    context = {
        'user': user
    }
    return render(request, 'edit_line_username.html', context)

# ユーザー名の更新処理を行うビュー
def update_line_username(request, user_id):
    if request.method == 'POST':
        account = get_object_or_404(LineAccount, user_id=user_id)
        new_display_name = request.POST.get('display_name')

        if new_display_name and account.display_name != new_display_name:
            account.display_name = new_display_name
            account.save()

    return redirect('dashboard') 


@method_decorator(login_required(login_url='/'), name='dispatch')
class DashboardView(View):
    template_name='dashboard.html'

    def get(self, request, *args, **kwargs):
        context = {}

        # 団体名の表示
        context['current_user'] = request.user

        # 並び替えフィルター
        sort_option = request.GET.get('sort', 'name-asc')
        if sort_option == 'name-asc':
            line_users = LineAccount.objects.all().order_by('display_name')
        elif sort_option == 'latest-date':
            line_users = LineAccount.objects.annotate(last_sent=Max('linemessage__last_sent_date')).order_by('-last_sent')
        context['sort_option'] = sort_option

        # 検索バー
        query = request.GET.get('q','')
        if query:
            line_users = LineAccount.objects.filter(display_name__icontains=query)
        else:
            line_users = LineAccount.objects.all()
        context['search_query'] = query

        # 絞り込みフィルター
        filter_option = request.GET.get('filter', None)
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
                        'created_at': user.created_at,
                        'user_id':user.user_id
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
                    'created_at': user.created_at,
                    'user_id':user.user_id
                })
        context['users_with_last_message'] = users_with_last_message
        context['filter_option'] = filter_option

        return render(request, self.template_name, context)

class LogoutView(LogoutView):
    template_name='logout.html'

#設定画面
def settings_view(request):
    return render(request, 'setting.html')