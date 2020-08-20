# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=R0201
# pylint: disable=R0903
# pylint: disable=W0621
from decimal import Decimal

import datetime
import pytest
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.utils import timezone

from ..models import Order, OrderItem


pytestmark = pytest.mark.django_db


@pytest.fixture
def order():
    """Return a new, empty Order record, saved to DB."""
    record = Order(coordinator='Bernd', restaurant_name='Hallo Pizza')
    record.save()
    return record


@pytest.fixture
def another_order():
    """Return a new, empty Order record, saved to DB."""
    record = Order(coordinator='Bernd', restaurant_name='Pizza Hut')
    record.save()
    return record


class TestOrderValidation:  # noqa
    def test_order_accepts_url_with_correct_format(self):
        order = Order(
            coordinator='Bernd',
            restaurant_name='Hallo Pizza',
            restaurant_url='http://www.hallopizza.de/'
        )
        # slug is required but will auto-generated only when save() is called but its not needed for this test
        order.full_clean(exclude=['slug'])
        assert order.restaurant_url == 'http://www.hallopizza.de/'

    def test_order_rejects_url_with_incorrect_format(self):
        order = Order(
            coordinator='Bernd',
            restaurant_name='Hallo Pizza',
            restaurant_url='hurensohn'
        )
        with pytest.raises(ValidationError):
            order.full_clean(exclude=['slug'])


class TestOrderCreation:
    def test_new_order_has_slug(self, order):
        assert order.slug

    def test_new_order_has_preparing_state(self, order):
        assert order.is_preparing is True

    def test_order_can_store_url(self):
        order = Order(
            coordinator='Bernd',
            restaurant_name='Hallo Pizza',
            restaurant_url='http://www.hallopizza.de/'
        )
        order.save()
        assert order.restaurant_url == 'http://www.hallopizza.de/'

    def test_order_restaurant_name_does_not_have_to_be_unique_per_user(self):
        Order(coordinator='Bernd', restaurant_name='Hallo Pizza').save()
        Order(coordinator='Bernd', restaurant_name='Hallo Pizza').save()


class TestOrderPreparationExpiry:
    @staticmethod
    def create_order(expires_after):
        record = Order(
            coordinator='Bernd',
            restaurant_name='Hallo Pizza',
            preparation_expires_after=expires_after
        )
        record.save()
        return record

    def test_preparation_expiry_must_be_in_the_future(self):
        record = Order(
            coordinator='Bernd',
            restaurant_name='Hallo Pizza',
            preparation_expires_after=datetime.timedelta(minutes=-10)
        )
        with pytest.raises(ValueError):
            record.save()

    def test_order_determines_if_not_expired(self):
        expire_after = datetime.timedelta(minutes=10)
        order = self.create_order(expire_after)
        time_in_future = timezone.now() + datetime.timedelta(minutes=5)
        is_expired = order.is_preparation_time_expired(time_in_future)
        assert is_expired is False

    def test_order_determines_if_expired(self):
        expire_after = datetime.timedelta(minutes=10)
        order = self.create_order(expire_after)
        time_in_future = timezone.now() + expire_after + datetime.timedelta(minutes=5)
        is_expired = order.is_preparation_time_expired(time_in_future)
        assert is_expired is True

    def test_order_does_not_switch_when_order_is_not_expired(self):
        expire_after = datetime.timedelta(minutes=10)
        order = self.create_order(expire_after)
        time_in_future = timezone.now() + datetime.timedelta(minutes=5)
        order.ordering_when_expired(time_in_future)
        assert order.is_preparing is True
        assert order.is_ordering is False

    def test_order_switches_to_ordering_when_order_is_expired(self):
        expire_after = datetime.timedelta(minutes=10)
        order = self.create_order(expire_after)
        time_in_future = timezone.now() + expire_after + datetime.timedelta(minutes=5)
        order.ordering_when_expired(time_in_future)
        assert order.is_preparing is False
        assert order.is_ordering is True


class TestOrderStateSwitching:
    def test_order_state_can_be_switched_to_delivery(self, order):
        order.ordering()
        assert order.is_ordering is True
        order.ordered()
        assert order.is_ordered is True
        order.delivered()
        assert order.is_delivered is True

    def test_order_history_is_maintained_for_state_changes(self, order):
        # forgive me for being lazy
        order.ordering()
        order.ordered()
        order.delivered()
        state_changes = order.history.all()
        assert len(state_changes) == 3


class TestOrderCancellation:
    def test_order_cancellation_requires_reason(self, order):
        with pytest.raises(ValueError):
            order.cancel(reason=None)

    def test_order_cancellation_reason_is_propagated_to_history(self, order):
        order.cancel(reason='Fuck you')
        assert order.history.all().last().reason == 'Fuck you'

    def test_order_can_be_canceled_while_order_is_prepared(self, order):
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    def test_order_can_be_canceled_while_order_is_ordered(self, order):
        order.ordering()
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    def test_order_can_be_canceled_while_order_is_delivered(self, order):
        order.ordering()
        order.ordered()
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    def test_order_cannot_be_canceled_after_order_is_delivered(self, order):
        order.ordering()
        order.ordered()
        order.delivered()
        with pytest.raises(ValueError):
            order.cancel(reason='Fuck you')


class TestOrderItemCreation:
    def test_orderitem_can_be_added_and_retrieved_while_order_is_prepared(self, order):
        order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        assert order.items.count() == 1

    def test_orderitem_cannot_be_added_after_order_is_prepared(self, order):
        order.ordering()
        with pytest.raises(ValueError):
            order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order.ordered()
        with pytest.raises(ValueError):
            order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order.delivered()
        with pytest.raises(ValueError):
            order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)

    def test_orderitem_cannot_be_changed_after_order_is_prepared(self, order):
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

    def test_orderitem_cannot_be_deleted_after_order_preparation(self, order):
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

    def test_new_orderitem_has_slug(self, order):
        item = order.items.create(participant='Bernd', description='Pizza Salami', price=Decimal('5.60'), amount=1)
        assert item.slug == 'bernd-pizza-salami'

    def test_new_orderitem_has_item_data(self, order):
        order.items.create(participant='Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order_item = order.items.get()
        assert order_item.participant == 'Kevin'
        assert order_item.price == Decimal('7.20')
        assert order_item.amount == 1

    def test_order_returns_all_items(self, order):
        order.items.create(participant='Kevin', description='Test1', price=Decimal('7.21'), amount=1)
        order.items.create(participant='Kevin', description='Test2', price=Decimal('7.22'), amount=1)
        order.items.create(participant='Kevin', description='Test3', price=Decimal('7.23'), amount=1)
        order.items.create(participant='Kevin', description='Test4', price=Decimal('7.24'), amount=1)
        assert order.items.count() == 4

    def test_user_can_have_same_order_items_in_different_orders(self, order, another_order):
        order.items.create(participant='Bernd', description='Pizza Salami', price=Decimal('5.60'), amount=1)
        another_order.items.create(participant='Bernd', description='Pizza Salami', price=Decimal('5.60'), amount=1)
        assert order.items.count() == 1
        assert another_order.items.count() == 1

    def test_orderitem_description_must_be_unique_per_order_and_user(self, order):
        # need nested atomic blocks otherwise django complains: You can't execute queries until the end of the 'atomic'
        # block.
        with transaction.atomic():
            order.items.create(participant='Bernd', description='Pizza Salami', price=Decimal('5.60'), amount=1)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                order.items.create(participant='Bernd', description='Pizza Salami', price=Decimal('5.60'), amount=1)
        assert order.items.count() == 1


class TestItemPriceCalculation:
    def test_order_total_price_sums_all_orderitem_total_prices(self, order):
        order.items.create(participant='Kevin', description='Test1', price=Decimal('7.21'), amount=1)
        order.items.create(participant='Kevin', description='Test2', price=Decimal('7.22'), amount=1)
        order.items.create(participant='Kevin', description='Test3', price=Decimal('7.23'), amount=1)
        order.items.create(participant='Kevin', description='Test4', price=Decimal('7.24'), amount=2)
        assert order.total_price == Decimal('36.14')

    def test_orderitem_total_price_multiplies_price_and_amount(self):
        item = OrderItem(price=Decimal('7.2'), amount=3)
        assert item.total_price == Decimal('21.6')
