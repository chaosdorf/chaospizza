# pylint: disable=C0111
# pylint: disable=R0903
import pytest
from ..models import Order
from ..mixins import UserSessionMixin


class DummyRequest:
    def __init__(self):
        self.session = {}


class TestUserSessionMixin:
    class View(UserSessionMixin):
        def __init__(self):
            self.request = DummyRequest()

    @pytest.fixture
    def view(self):
        return TestUserSessionMixin.View()

    @pytest.fixture
    def order1(self):
        # simulate slug to avoid db access
        return Order(id=1, coordinator='Hugo', restaurant_name='Hallo Pizza', slug='hugo-hallo-pizza')

    @pytest.fixture
    def order2(self):
        # simulate slug to avoid db access
        return Order(id=2, coordinator='Detlef', restaurant_name='Pizza Hut', slug='hugo-hallo-pizza')

    def test_coordinator_name_can_be_stored_and_retrieved(self, view):  # noqa
        view.username = 'Hugo'
        assert view.username == 'Hugo'

    def test_user_is_not_coordinator_in_empty_session(self, view):  # noqa
        assert view.is_coordinator is False

    def test_user_is_coordinator_after_init(self, view, order1):  # noqa
        view.add_order_to_session(order1)
        assert view.is_coordinator is True

    def test_order_slug_is_stored_in_session_after_init(self, view, order1):  # noqa
        view.add_order_to_session(order1)
        assert view.request.session['order_slug'] == 'hugo-hallo-pizza'

    def test_user_is_allowed_to_edit_created_order_after_init(self, view, order1):  # noqa
        view.add_order_to_session(order1)
        assert view.user_can_edit_order(order1.id) is True

    def test_user_is_not_allowed_to_edit_other_orders(self, view, order1, order2):  # noqa
        view.add_order_to_session(order1)
        assert view.user_can_edit_order(order2.id) is False

    def test_user_is_not_coordinator_after_disable(self, view, order1):  # noqa
        view.add_order_to_session(order1)
        view.remove_order_from_session()
        assert view.is_coordinator is False

    def test_user_can_not_edit_order_after_disable(self, view, order1):  # noqa
        view.add_order_to_session(order1)
        view.remove_order_from_session()
        assert view.user_can_edit_order(order1.id) is False

    def test_user_is_allowed_to_edit_own_order_items(self, view):
        view.add_order_item_to_session(1, 1)
        view.add_order_item_to_session(2, 4)
        assert view.user_can_edit_order_item(1, 1) is True
        assert view.user_can_edit_order_item(2, 4) is True

    def test_user_is_not_allowed_to_edit_other_order_items(self, view):
        view.add_order_item_to_session(1, 10)
        view.add_order_item_to_session(2, 10)
        assert view.user_can_edit_order_item(1, 1) is False
        assert view.user_can_edit_order_item(2, 4) is False
