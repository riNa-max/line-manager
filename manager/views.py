from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from linebot import LineBotApi,WebhookHandler
from linebot.models import MessageEvent,TextMessage,ImageMessage
from config.settings import LINE_ACCESS_TOKEN,LINE_SECRET_KEY

from .models import LineAccount,LineMessage

line_bot_api=LineBotApi(LINE_ACCESS_TOKEN)
handler=WebhookHandler(LINE_SECRET_KEY)

@method_decorator(csrf_exempt, name='dispatch')
class Linewebhook(View):
    def post(self,request,*args,**kwargs):
        signature=request.headers["X-Line-Signature"]
        body=request.body.decode("utf-8")

        try:
            handler.handle(body,signature)
        except KeyError:
            return HttpResponse(status=400)
        
        return HttpResponse(status=200)

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    message_type=event.message.type
    user_id=event.source.user_id
    message_id=event.message.id

    profile=line_bot_api.get_profile(user_id)
    display_name=profile.display_name

    # LineAccountを取得するか、新規作成（存在しない場合）
    account, created = LineAccount.objects.get_or_create(
        user_id=user_id,
        defaults={'display_name': display_name}
    )

    # LineMessageを作成してデータベースに保存
    LineMessage.objects.create(
        user=account,            # ForeignKeyとしてLineAccountを設定
        message_id=message_id,   # メッセージIDを設定
        message_type=message_type  # メッセージタイプを設定
    )

@handler.add(MessageEvent,message=ImageMessage)
def handle_image_message(event):
    message_id=event.message.id
    message_type=event.message.type
    user_id=event.source.user_id

    profile=line_bot_api.get_profile(user_id)
    display_name=profile.display_name

    LineAccount.objects.create(
        user_id=user_id,
        display_name=display_name
    )
    # LineAccountを取得するか、新規作成（存在しない場合）
    account, created = LineAccount.objects.get_or_create(
        user_id=user_id,
        defaults={'display_name': display_name}
    )

    # LineMessageを作成してデータベースに保存
    LineMessage.objects.create(
        user=account,            # ForeignKeyとしてLineAccountを設定
        message_id=message_id,   # メッセージIDを設定
        message_type=message_type  # メッセージタイプを設定
    )
