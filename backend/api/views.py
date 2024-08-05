from rest_framework import generics, viewsets
from .serializers import *
from .models import *

class EmailLetterViesSet(viewsets.ModelViewSet):
    serializer_class = EmailLetterSerializer
    queryset = EmailLetter.objects.all()
