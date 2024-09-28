from django.db import models
from django.utils import timezone

class LineAccount(models.Model):
    user_id=models.CharField(max_length=255)
    display_name=models.CharField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.display_name} ({self.user_id}) - {self.created_at}"
    
class LineMessage(models.Model):
    user=models.ForeignKey(LineAccount,on_delete=models.CASCADE)
    message_id=models.CharField(max_length=255)
    message_type=models.CharField(max_length=255)
    last_sent_date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.user.display_name} ({self.message_id}) - {self.message_type}"