from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass


class EmailLetter(models.Model):
    sender = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE)
    topic = models.CharField(max_length=255, verbose_name="Тема письма")
    date_sent = models.DateField()
    date_received = models.DateField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)


class EmailLetterFile(models.Model):
    email_letter = models.ForeignKey(to='EmailLetter', on_delete=models.CASCADE, related_name='files')
    file = models.FileField()
    name = models.CharField(max_length=255, blank=True, null=True)
