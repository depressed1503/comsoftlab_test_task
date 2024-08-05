from rest_framework import serializers
from .models import *


class EmailLetterFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLetterFile
        fields = ('email_letter', 'file')


class EmailLetterSerializer(serializers.ModelSerializer):
    files = EmailLetterFileSerializer(many=True, required=False)

    class Meta:
        model = EmailLetter
        fields = ('topic', 'date_sent', 'date_received', 'text', 'files', 'sender')

    def to_representation(self, instance):
        print(instance)
        return super().to_representation(instance)
