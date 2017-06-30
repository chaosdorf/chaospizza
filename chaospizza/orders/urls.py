# pylint: disable=C0103
# pylint: disable=C0111
from django.conf.urls import url
from .views import (
    ListOrders, CreateOrder, ViewOrder, UpdateOrderState, CancelOrder,
    CreateOrderItem, UpdateOrderItem, DeleteOrderItem
)


app_name = 'orders'
urlpatterns = [
    url(
        r'^$', ListOrders.as_view(),
        name='list_orders'
    ),
    url(
        r'^create$', CreateOrder.as_view(),
        name='create_order'
    ),
    url(
        r'^order/(?P<order_slug>[0-9]+)/item/(?P<item_slug>[0-9]+)/update', UpdateOrderItem.as_view(),
        name='update_orderitem'
    ),
    url(
        r'^order/(?P<order_slug>[0-9]+)/item/(?P<item_slug>[0-9]+)/delete', DeleteOrderItem.as_view(),
        name='delete_orderitem'
    ),
    url(
        r'^order/(?P<order_slug>[0-9]+)/item/create', CreateOrderItem.as_view(),
        name='create_orderitem'
    ),
    url(
        r'^order/(?P<order_slug>[0-9]+)/update-state', UpdateOrderState.as_view(),
        name='update_state'
    ),
    url(
        r'^order/(?P<order_slug>[0-9]+)/cancel', CancelOrder.as_view(),
        name='cancel_order'
    ),
    url(
        r'^order/(?P<order_slug>[0-9]+)/', ViewOrder.as_view(),
        name='view_order'
    ),
]
