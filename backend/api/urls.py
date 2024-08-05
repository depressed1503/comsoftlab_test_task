from django.urls import path, include
from rest_framework import routers
from .views import *


email_letter_router = routers.SimpleRouter()
email_letter_router.register(r'letters', EmailLetterViesSet)
urlpatterns = [
    path('email/', include(email_letter_router.urls)),
    path('auth/', include('rest_framework.urls'))
]