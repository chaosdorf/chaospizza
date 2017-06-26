# pylint: disable=C0111
from django.conf.urls import url
from .views import menu_home


urlpatterns = [
    url(r'^$', menu_home),
]
