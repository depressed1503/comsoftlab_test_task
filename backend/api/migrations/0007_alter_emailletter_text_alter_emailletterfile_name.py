# Generated by Django 4.2.5 on 2024-08-06 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_emailletter_date_received'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailletter',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='emailletterfile',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
