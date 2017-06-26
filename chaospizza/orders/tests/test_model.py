# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=R0201
from decimal import Decimal
import pytest

from ..models import Order


class TestOrderModel:
    @pytest.fixture
    def order(self):
        """Return a new, empty Order instance, saved to DB."""
        order = Order(coordinator='Bernd', restaurant_name='Yolo')
        order.save()
        return order

    @pytest.mark.django_db
    def test_new_order_has_preparing_state(self):  # noqa
        order = Order(coordinator='Bernd', restaurant_name='Yolo')
        order.save()
        assert order.state == 'preparing'

    @pytest.mark.django_db
    def test_added_order_item_is_associated_with_order_and_user(self, order):  # noqa
        order.add_item('Kevin', description='Test', price=Decimal('7.20'), amount=1)

        order_item = order.items().get()
        assert order_item.participant == 'Kevin'

    @pytest.mark.django_db
    def test_order_returns_all_items(self, order):  # noqa
        order.add_item('Kevin', description='Test1', price=Decimal('7.21'), amount=1)
        order.add_item('Kevin', description='Test2', price=Decimal('7.22'), amount=1)
        order.add_item('Kevin', description='Test3', price=Decimal('7.23'), amount=1)
        order.add_item('Kevin', description='Test4', price=Decimal('7.24'), amount=1)

        number_of_items = order.items().count()
        assert number_of_items == 4
