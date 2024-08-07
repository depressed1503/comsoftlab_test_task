# Generated by Django 4.2.5 on 2024-08-07 19:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_emailletter_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailletter',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='email_letters', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
