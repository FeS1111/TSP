# Generated by Django 5.2 on 2025-04-10 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_user_last_login'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='user_id',
            new_name='id',
        ),
    ]
