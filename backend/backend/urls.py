from django.contrib import admin
from django.urls import include, path
from api.urls import urlpatterns
from django.conf.urls.static import static
from .settings import MEDIA_ROOT, MEDIA_URL


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(urlpatterns)),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
