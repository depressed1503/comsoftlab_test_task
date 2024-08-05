from django.contrib import admin
from django.urls import include, path
from api.urls import urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(urlpatterns))
]
