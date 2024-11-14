from django.core.management.base import BaseCommand
from manager.models import LineMessage
from views import notify_inactive_users_to_admin
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "3か月以上アクティブでないユーザーを管理者に通知します"

    def handle(self, request, *args, **kwargs):
        three_months_ago = timezone.now() - timedelta(days=90)
        inactive_users = []

        user_line_accounts = request.user.line_accounts.all()
        for account in user_line_accounts:
            last_message = LineMessage.objects.filter(user=account).order_by('-last_sent_date').first()
            if last_message and last_message.last_sent_date < three_months_ago:
                inactive_users.append({
                    'user': account.display_name,
                    'last_sent_date': last_message.last_sent_date,
                })

        notify_inactive_users_to_admin(inactive_users)
