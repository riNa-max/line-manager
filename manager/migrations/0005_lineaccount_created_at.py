# Generated by Django 5.1.1 on 2024-09-20 08:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_remove_lineaccount_last_sent_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineaccount',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
