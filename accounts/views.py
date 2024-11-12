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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

class AccountLoginView(LoginView):
    template_name='login.html'
    form_class=LoginForm

    def get_success_url(self):
        return reverse_lazy('dashboard')

# 管理者に通知する関数
def notify_inactive_users_to_admin(request,inactive_users):

    line_access_token = request.user.access_token
    admin_line_id = request.user.line_user_id
    secret_key=request.user.secret_key

# trueにしてみる
    if not line_access_token or not admin_line_id or not secret_key:
        # トークンまたはユーザーID、シークレットキーが設定されていない場合は処理を終了
        print(f"{request.user} は LINE の設定が不足しているため、通知をスキップしました。")
        return redirect('dashboard')


    line_bot_api=LineBotApi(request.user.access_token)
    
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

        # ログイン中のユーザーのLineAccountを取得
        user_line_accounts = request.user.line_accounts.all()
        context['line_accounts'] = user_line_accounts

        # 並び替えフィルター
        sort_option = request.GET.get('sort', 'name-asc')
        if sort_option == 'name-asc':
            line_users = user_line_accounts.order_by('display_name')
        elif sort_option == 'latest-date':
            line_users = user_line_accounts.annotate(last_sent=Max('linemessage__last_sent_date')).order_by('-last_sent')
        context['sort_option'] = sort_option

        # 検索バー
        query = request.GET.get('q','')
        if query:
            line_users = user_line_accounts.filter(display_name__icontains=query)
        else:
            line_users = user_line_accounts
        context['search_query'] = query

        # 絞り込みフィルター
        filter_option = request.GET.get('filter', None)
        three_months_ago = timezone.now() - timedelta(days=10)

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

        notify_inactive_users_to_admin(request,inactive_users)
            
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):

        line_access_token = request.user.access_token
        admin_line_id = request.user.line_user_id
        secret_key=request.user.secret_key

        if not line_access_token or not admin_line_id or not secret_key:
        # トークンまたはユーザーID、シークレットキーが設定されていない場合は処理を終了
            print(f"{request.user} は LINE の設定が不足しているため、通知をスキップしました。")
            return redirect('dashboard')


        line_bot_api=LineBotApi(request.user.access_token)
        admin_user_id = request.user.line_user_id

        # 3か月以上メッセージを送信していないユーザーを通知する処理
        three_months_ago = timezone.now() - timedelta(days=10)
        inactive_users = LineAccount.objects.filter(
            linemessage__last_sent_date__lt=three_months_ago
        ).distinct()

        # 名簿作成
        if inactive_users.exists():
            user_list = "\n".join([f"{user.display_name}" for user in inactive_users])
            message_text = f"3ヶ月以上メッセージを送信していないユーザー:\n{user_list}"
        else:
            message_text = "3ヶ月以上メッセージを送信していないユーザーはいません。"

        # 管理者にLINE通知を送信
        try:
            line_bot_api.push_message(admin_user_id, TextSendMessage(text=message_text))
            messages.success(request, '管理者に通知を送信しました。')
        except Exception as e:
            messages.error(request, f"通知の送信中にエラーが発生しました: {e}")
            print(f"エラー発生: {e}")

        return redirect('dashboard')

class LogoutView(LogoutView):
    template_name='logout.html'

#設定画面
def settings_view(request):
    return render(request, 'setting.html')