# pylint: disable=C0111
from django.conf.urls import url
from .views import home


urlpatterns = [
    url(r'^$', home),
]
