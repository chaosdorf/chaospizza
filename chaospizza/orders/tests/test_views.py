# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=R0201
# pylint: disable=R0903
import pytest
from ..models import Order
from ..views import CoordinatorSessionMixin


class DummyRequest():
    def __init__(self):
        self.session = {}


class DummyView(CoordinatorSessionMixin):
    def __init__(self):
        self.request = DummyRequest()


class TestCoordinatorSessionMixin:
    @pytest.fixture
    def view(self):
        """Returns a DummyView instance with the mixin."""
        return DummyView()

    def test_user_is_not_coordinator_in_empty_session(self, view):  # noqa
        state = view.is_coordinator()
        assert state is False

    def test_user_is_coordinator_after_init(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        state = view.is_coordinator()
        assert state is True

    def test_orderid_is_set_after_init(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        order_id = view.coordinated_order_id()
        assert order_id == 1

    def test_coordinator_name_can_be_retrieved_after_init(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        name = view.coordinator_name()
        assert name == 'Hugo'

    def test_user_is_not_coordinator_after_disable(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        view.disable_order_coordination()
        state = view.is_coordinator()
        assert state is False
