# pylint: disable=C0111
from django.conf.urls import re_path
from .views import menu_home


urlpatterns = [
    re_path(r'^$', menu_home, name='menu_home'),
]
