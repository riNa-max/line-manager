from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Account(AbstractUser):
    channel_id=models.CharField(max_length=255,null=True,blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    secret_key = models.CharField(max_length=255, null=True, blank=True)
    line_user_id = models.CharField(max_length=255, null=True, blank=True)