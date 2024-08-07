from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    email = models.EmailField(unique=True)
    email_password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.email_password:
            self.email_password = self.password
        return super(CustomUser, self).save(*args, **kwargs)


class EmailLetter(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='email_letters')
    sender = models.EmailField(unique=False)
    topic = models.CharField(max_length=255, verbose_name="Тема письма")
    date_sent = models.DateField()
    date_received = models.DateField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    uid = models.CharField(max_length=255, null=True, blank=True, unique=True)


class EmailLetterFile(models.Model):
    email_letter = models.ForeignKey(to='EmailLetter', on_delete=models.CASCADE, related_name='files')
    file = models.FileField()
    name = models.CharField(max_length=255, blank=True, null=True)
