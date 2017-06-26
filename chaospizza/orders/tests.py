# pylint: disable=C0111
# pylint: disable=R0201
from decimal import Decimal
import pytest

from django.contrib.auth.models import User
from .models import Order, OrderItem


@pytest.mark.django_db
def test_my_user():
    """Test basic SQL query."""
    coordinator = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    user = User.objects.create_user('seth', 'seth@thebeatles.com', 'sethpassword')

    order = Order(coordinator=coordinator, restaurant_name='Yolo')
    order.save()
    print(order.id)
    print(order.coordinator)
    assert order.state == 'preparing'

    order.add_item(owner=user, description='hahaha', price=Decimal(7, 2), amount=1)

    order_item = OrderItem.objects.filter(order=order).get()
    print(order_item.description)

    raise ValueError("yolo")
