from django.urls import path, include
from rest_framework import routers
from .views import *
from .routing import websocket_urlpatterns

router = routers.SimpleRouter()
router.register(r'letters', EmailLetterViesSet)
router.register(r'files', EmailLetterFileViewSet)

urlpatterns = [
    path('email/', include(router.urls)),
    path('auth/login/', CustomLoginView.as_view()),
    path('auth/user/', get_current_user),
    path('csrf/', get_csrf_token),
] + websocket_urlpatterns
