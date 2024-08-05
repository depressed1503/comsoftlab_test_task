from rest_framework import viewsets
from .serializers import *
from .models import *


class EmailLetterViesSet(viewsets.ModelViewSet):
    serializer_class = EmailLetterSerializer
    queryset = EmailLetter.objects.all()


class EmailLetterFileViewSet(viewsets.ModelViewSet):
    serializer_class = EmailLetterFileSerializer
    queryset = EmailLetterFile.objects.all()
