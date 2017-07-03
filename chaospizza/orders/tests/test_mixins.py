# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=R0201
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
        return Order(id=1, coordinator='Hugo')

    @pytest.fixture
    def order2(self):
        return Order(id=2, coordinator='Detlef')

    def test_coordinator_name_can_be_stored_and_retrieved(self, view):  # noqa
        view.username = 'Hugo'
        assert view.username == 'Hugo'

    def test_user_is_not_coordinator_in_empty_session(self, view):  # noqa
        assert view.is_coordinator is False

    def test_user_is_coordinator_after_init(self, view, order1):  # noqa
        view.enable_order_coordination(order1)
        assert view.is_coordinator is True

    def test_user_is_allowed_to_edit_created_order_after_init(self, view, order1):  # noqa
        view.enable_order_coordination(order1)
        assert view.user_can_edit(order1.id) is True

    def test_user_is_not_allowed_to_edit_other_orders(self, view, order1, order2):  # noqa
        view.enable_order_coordination(order1)
        assert view.user_can_edit(order2.id) is False

    def test_user_is_not_coordinator_after_disable(self, view, order1):  # noqa
        view.enable_order_coordination(order1)
        view.disable_order_coordination()
        assert view.is_coordinator is False

    def test_user_can_not_edit_order_after_disable(self, view, order1):  # noqa
        view.enable_order_coordination(order1)
        view.disable_order_coordination()
        assert view.user_can_edit(order1.id) is False
