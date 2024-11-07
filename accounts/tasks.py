from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from linebot import LineBotApi
from linebot.models import TextSendMessage
from manager.models import LineAccount, LineMessage
from config.settings import LINE_ACCESS_TOKEN,LINE_USER_ID

# LINE Bot APIの設定
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

@shared_task
def notify_inactive_users():
    three_months_ago = timezone.now() - timedelta(days=90)
    inactive_users = LineAccount.objects.filter(
        linemessage__last_sent_date__lt=three_months_ago
    ).distinct()
    
    if inactive_users.exists():
        user_list = "\n".join([f"{user.display_name} (ID: {user.user_id})" for user in inactive_users])
        message_text = f"3ヶ月以上メッセージを送信していないユーザー:\n{user_list}"
    else:
        message_text = "3ヶ月以上メッセージを送信していないユーザーはいません。"
    
    admin_user_id = LINE_USER_ID
    try:
        line_bot_api.push_message(admin_user_id, TextSendMessage(text=message_text))
    except Exception as e:
        print(f"LINE通知の送信中にエラーが発生しました: {e}")
