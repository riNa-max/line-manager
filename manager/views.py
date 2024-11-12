from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from linebot import LineBotApi,WebhookHandler
from linebot.models import MessageEvent,TextMessage,ImageMessage
# from config.settings import LINE_ACCESS_TOKEN,LINE_SECRET_KEY

from .models import LineAccount,LineMessage
from accounts.models import Account

@method_decorator(csrf_exempt, name='dispatch')
class Linewebhook(View):
    def post(self,request,channel_id,*args,**kwargs):

        try:
            account=Account.objects.get(channel_id=channel_id)
        except:
            return HttpResponse(status=400)

        line_bot_api=LineBotApi(account.access_token)
        handler=WebhookHandler(account.secret_key)

        signature=request.headers["X-Line-Signature"]
        body=request.body.decode("utf-8")

        try:
            events=handler.parser.parse(body,signature)
            for event in events:
                if isinstance(event,MessageEvent):
                    message_type=event.message.type
                    user_id=event.source.user_id
                    message_id=event.message.id

                    profile=line_bot_api.get_profile(user_id)
                    display_name=profile.display_name

                    # LineAccountを取得するか、新規作成（存在しない場合）
                    line_account, created = LineAccount.objects.get_or_create(
                        user_id=user_id,
                        defaults={'display_name': display_name},administrator=account
                    )

                    # LineMessageを作成してデータベースに保存
                    LineMessage.objects.create(
                        user=line_account,            # ForeignKeyとしてLineAccountを設定
                        message_id=message_id,   # メッセージIDを設定
                        message_type=message_type,  # メッセージタイプを設定
                        administrator=account,
                    )

        except Exception as e:
            print(e)
            return HttpResponse(status=400)

        print(account)
        
        return HttpResponse(status=200)

