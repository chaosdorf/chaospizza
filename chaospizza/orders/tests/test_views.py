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

    def test_is_coordinator_returns_false_on_empty_session(self, view):  # noqa
        state = view.is_coordinator()

        assert state is False

    def test_is_coordinator_returns_true_after_init(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        state = view.is_coordinator()
        assert state is True

    def test_is_coordinator_returns_false_after_disable(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        view.disable_order_coordination()
        state = view.is_coordinator()
        assert state is False

    # TODO test id and name
