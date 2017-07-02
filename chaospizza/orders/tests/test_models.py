# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=R0201
# pylint: disable=R0903
from decimal import Decimal
import pytest

from ..models import Order, OrderItem


class TestOrder:
    @pytest.fixture
    def order(self):
        """Return a new, empty Order instance, saved to DB."""
        order = Order(coordinator='Bernd', restaurant_name='Yolo')
        order.save()
        return order

    # TODO find library to automate tedious state machine testing

    @pytest.mark.django_db
    def test_new_order_has_preparing_state(self, order):  # noqa
        assert order.is_preparing is True

    @pytest.mark.django_db
    def test_order_state_can_be_switched_to_delivery(self, order):  # noqa
        order.ordering()
        assert order.is_ordering is True
        order.ordered()
        assert order.is_ordered is True
        order.delivered()
        assert order.is_delivered is True

    @pytest.mark.django_db
    def test_order_cancellation_requires_reason(self, order):  # noqa
        with pytest.raises(ValueError):
            order.cancel(reason=None)

    @pytest.mark.django_db
    def test_order_can_be_canceled_while_preparing(self, order):  # noqa
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    @pytest.mark.django_db
    def test_order_can_be_canceled_while_ordering(self, order):  # noqa
        order.ordering()
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    @pytest.mark.django_db
    def test_order_can_be_canceled_while_ordered(self, order):  # noqa
        order.ordering()
        order.ordered()
        order.cancel(reason='Fuck you')
        assert order.is_canceled is True

    @pytest.mark.django_db
    def test_order_cannot_be_canceled_after_delivered(self, order):  # noqa
        order.ordering()
        order.ordered()
        order.delivered()
        with pytest.raises(ValueError):
            order.cancel(reason='Fuck you')

    @pytest.mark.django_db
    def test_order_item_can_be_added_and_retrieved_after_order_creation(self, order):  # noqa
        order.add_item('Kevin', description='Test', price=Decimal('7.20'), amount=1)
        assert order.items().count() == 1

    @pytest.mark.django_db
    def test_order_item_cannot_be_added_after_preparing(self, order):  # noqa
        # TODO find way to prevent stupid developers from messing with OrderItem records directly
        order.ordering()
        with pytest.raises(ValueError):
            order.add_item('Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order.ordered()
        with pytest.raises(ValueError):
            order.add_item('Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order.delivered()
        with pytest.raises(ValueError):
            order.add_item('Kevin', description='Test', price=Decimal('7.20'), amount=1)

    @pytest.mark.skip(reason='not yet implemented')
    @pytest.mark.django_db
    def test_order_item_cannot_be_changed_after_preparing(self, order):  # noqa
        # TODO need order.update_item() which checks order state
        pass

    @pytest.mark.skip(reason='not yet implemented')
    @pytest.mark.django_db
    def test_order_item_cannot_be_deleted_after_preparing(self, order):  # noqa
        # TODO need order.delete_item() which checks order state
        pass

    @pytest.mark.django_db
    def test_history_is_maintained_for_state_changes(self, order):  # noqa
        # forgive me for being lazy
        order.ordering()
        order.ordered()
        order.delivered()
        state_changes = order.history()
        assert len(state_changes) == 3

    @pytest.mark.django_db
    def test_added_order_item_is_associated_with_correct_data(self, order):  # noqa
        order.add_item('Kevin', description='Test', price=Decimal('7.20'), amount=1)
        order_item = order.items().get()
        assert order_item.participant == 'Kevin'
        assert order_item.price == Decimal('7.20')
        assert order_item.amount == 1

    @pytest.mark.django_db
    def test_order_returns_all_items(self, order):  # noqa
        order.add_item('Kevin', description='Test1', price=Decimal('7.21'), amount=1)
        order.add_item('Kevin', description='Test2', price=Decimal('7.22'), amount=1)
        order.add_item('Kevin', description='Test3', price=Decimal('7.23'), amount=1)
        order.add_item('Kevin', description='Test4', price=Decimal('7.24'), amount=1)
        number_of_items = order.items().count()
        assert number_of_items == 4

    @pytest.mark.django_db
    def test_order_calculates_total_price(self, order):  # noqa
        order.add_item('Kevin', description='Test1', price=Decimal('7.21'), amount=1)
        order.add_item('Kevin', description='Test2', price=Decimal('7.22'), amount=1)
        order.add_item('Kevin', description='Test3', price=Decimal('7.23'), amount=1)
        order.add_item('Kevin', description='Test4', price=Decimal('7.24'), amount=2)
        total_price = order.total_price()
        assert total_price == Decimal('36.14')


class TestOrderItem:
    def test_orderitem_calculates_total_price(self):  # noqa
        item = OrderItem(price=Decimal('7.2'), amount=3)
        total_price = item.total_price()
        assert total_price == Decimal('21.6')
