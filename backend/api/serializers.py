from rest_framework import serializers
from .models import *


class EmailLetterFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLetterFile
        fields = ('email_letter', 'file', 'name')

    def to_internal_value(self, data):
        data['name'] = data.get('file').name if data.get('file') else ''
        data['email_letter'] = data.get('email_letter')
        return super().to_internal_value(data)


class EmailLetterSerializer(serializers.ModelSerializer):
    files = EmailLetterFileSerializer(many=True, required=False)

    class Meta:
        model = EmailLetter
        fields = ('id', 'topic', 'date_sent', 'date_received', 'text', 'files', 'sender')


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')