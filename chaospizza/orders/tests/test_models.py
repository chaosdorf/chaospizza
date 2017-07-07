# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=R0201
# pylint: disable=R0903
from decimal import Decimal
import pytest
from django.db import IntegrityError

from ..models import Order, OrderItem


@pytest.mark.django_db
class TestOrder:
    @pytest.fixture
    def order(self):
        """Return a new, empty Order instance, saved to DB."""
        order = Order(coordinator='Bernd', restaurant_name='Hallo Pizza')
        order.save()
        return order

    # TODO find library to automate tedious state machine testing

    def test_new_order_has_slug(self, order):
        assert order.slug == 'bernd-hallo-pizza'

    def test_new_order_has_preparing_state(self, order):  # noqa
        assert order.is_preparing is True

    def test_restaurant_name_must_be_unique_per_user(self):
        Order(coordinator='Bernd', restaurant_name='Hallo Pizza').save()
        with pytest.raises(IntegrityError):
            Order(coordinator='Bernd', restaurant_name='Hallo Pizza').save()

    def test_order_state_can_be_switched_to_delivery(self, order):  # noqa
        order.ordering()
        assert order.is_ordering is True
        order.ordered()
        assert order.is_ordered is True
        order.delivered()
        assert order.is_delivered is True

    def test_order_cancellation_requires_reason(self, order):  # noqa
        with pytest.raises(ValueError):
            order.cancel(reason=None)

    def test_order_can_be_canceled_while_preparing(self, order):  # noqa
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    def test_order_can_be_canceled_while_ordering(self, order):  # noqa
        order.ordering()
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    def test_order_can_be_canceled_while_ordered(self, order):  # noqa
        order.ordering()
        order.ordered()
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    def test_order_cannot_be_canceled_after_delivered(self, order):  # noqa
        order.ordering()
        order.ordered()
        order.delivered()
        with pytest.raises(ValueError):
            order.cancel(reason='Fuck you')

    def test_order_item_can_be_added_and_retrieved_after_order_creation(self, order):  # noqa
        order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        assert order.items.count() == 1

    def test_order_item_cannot_be_added_after_preparing(self, order):  # noqa
        order.ordering()
        with pytest.raises(ValueError):
            order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order.ordered()
        with pytest.raises(ValueError):
            order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order.delivered()
        with pytest.raises(ValueError):
            order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)

    def test_order_item_cannot_be_changed_after_preparing(self, order):  # noqa
        order_item = order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order.ordering()
        with pytest.raises(ValueError):
            order_item.description = 'yolo'
            order_item.save()
        order.ordered()
        with pytest.raises(ValueError):
            order_item.description = 'bla'
            order_item.save()
        order.delivered()
        with pytest.raises(ValueError):
            order_item.description = 'asd'
            order_item.save()

    def test_order_item_cannot_be_deleted_after_preparing(self, order):  # noqa
        order_item = order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order.ordering()
        with pytest.raises(ValueError):
            order_item.delete()
        order.ordered()
        with pytest.raises(ValueError):
            order_item.delete()
        order.delivered()
        with pytest.raises(ValueError):
            order_item.delete()

    def test_history_is_maintained_for_state_changes(self, order):  # noqa
        # forgive me for being lazy
        order.ordering()
        order.ordered()
        order.delivered()
        state_changes = order.history.all()
        assert len(state_changes) == 3

    def test_added_order_item_is_associated_with_correct_data(self, order):  # noqa
        order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order_item = order.items.get()
        assert order_item.participant == 'Kevin'
        assert order_item.price == Decimal('7.20')
        assert order_item.amount == 1

    def test_order_returns_all_items(self, order):  # noqa
        order.items.create(participant='Kevin', description='Test1', price=Decimal('7.21'), amount=1)
        order.items.create(participant='Kevin', description='Test2', price=Decimal('7.22'), amount=1)
        order.items.create(participant='Kevin', description='Test3', price=Decimal('7.23'), amount=1)
        order.items.create(participant='Kevin', description='Test4', price=Decimal('7.24'), amount=1)
        number_of_items = order.items.count()
        assert number_of_items == 4

    def test_order_calculates_total_price(self, order):  # noqa
        order.items.create(participant='Kevin', description='Test1', price=Decimal('7.21'), amount=1)
        order.items.create(participant='Kevin', description='Test2', price=Decimal('7.22'), amount=1)
        order.items.create(participant='Kevin', description='Test3', price=Decimal('7.23'), amount=1)
        order.items.create(participant='Kevin', description='Test4', price=Decimal('7.24'), amount=2)
        assert order.total_price == Decimal('36.14')


@pytest.mark.django_db
class TestOrderItem:
    def test_new_orderitem_has_slug(self):
        order = Order(coordinator='Bernd', restaurant_name='Hallo Pizza')
        order.save()
        item = order.items.create(participant='Bernd', description='Pizza Salami', price=Decimal('5.60'), amount=1)
        assert item.slug == 'bernd-pizza-salami'

    def test_description_must_be_unique_per_user_and_order(self):
        order = Order(coordinator='Bernd', restaurant_name='Hallo Pizza')
        order.save()
        order.items.create(participant='Bernd', description='Pizza Salami', price=Decimal('5.60'), amount=1)
        with pytest.raises(IntegrityError):
            order.items.create(participant='Bernd', description='Pizza Salami', price=Decimal('5.60'), amount=1)

    def test_orderitem_calculates_total_price(self):  # noqa
        item = OrderItem(price=Decimal('7.2'), amount=3)
        assert item.total_price == Decimal('21.6')
