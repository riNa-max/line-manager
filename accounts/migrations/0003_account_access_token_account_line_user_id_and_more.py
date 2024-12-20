# Generated by Django 5.1.1 on 2024-11-10 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_account_channel_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='access_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='line_user_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='secret_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
