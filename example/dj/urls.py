import django
from django.urls import include, re_path as url
from django.conf import settings

from is_core.site import site


urlpatterns = [url(r'^', include(site.urls))]


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
