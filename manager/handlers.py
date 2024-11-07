from datetime import datetime
from django.utils import timezone
from .models import LineAccount, LineMessage, SentAccount
from accounts.models import Account

def handle_message_event(event):
    # イベントから送信者のLINEユーザーIDを取得
    line_user_id = event.source.user_id
    # メッセージIDや内容など、必要なデータを取得
    message_id = event.message.id
    message_type = event.message.type
    
    # LineAccountモデルから、該当のユーザーアカウントを取得
    try:
        line_account = LineAccount.objects.get(user_id=line_user_id)
    except LineAccount.DoesNotExist:
        # 該当のユーザーが存在しない場合は新規作成
        line_account = LineAccount.objects.create(user_id=line_user_id)

    # メッセージ情報を保存
    LineMessage.objects.create(
        user=line_account,
        message_id=message_id,
        message_type=message_type,
        last_sent_date=timezone.now()
    )

    # 管理者との紐付け処理
    # ここでは仮に管理者を取得する例として `administrator_id` を使用しています。
    administrator = Account.objects.get(id=event.administrator_id)  # 管理者IDを取得する方法に応じて変更してください
    
    # `SentAccount`に管理者とLINEアカウントの関係を保存
    SentAccount.objects.create(
        administrator=administrator,
        line_account=line_account,
        sent_at=timezone.now()
    )
