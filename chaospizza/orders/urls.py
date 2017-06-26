# pylint: disable=C0103
# pylint: disable=C0111
from django.conf.urls import url
from .views import ListOrders, CreateOrder, ViewOrder


app_name = 'orders'
urlpatterns = [
    url(r'^$', ListOrders.as_view(), name='list'),
    url(r'^create$', CreateOrder.as_view(), name='create'),
    url(r'^order/(?P<order_id>[0-9]+)', ViewOrder.as_view(), name='view'),
]
