# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=R0201
# pylint: disable=R0903
import pytest
from ..models import Order
from ..views import UserSessionMixin, CoordinatorSessionMixin


class DummyRequest():
    def __init__(self):
        self.session = {}


class TestUserSessionMixin:
    class View(UserSessionMixin):
        def __init__(self):
            self.request = DummyRequest()

    @pytest.fixture
    def view(self):
        """Returns a DummyView instance with the mixin."""
        return TestUserSessionMixin.View()

    def test_coordinator_name_can_be_stored_and_retrieved(self, view):  # noqa
        view.username = 'Hugo'
        assert view.username == 'Hugo'


class TestCoordinatorSessionMixin:
    class View(CoordinatorSessionMixin):
        def __init__(self):
            self.request = DummyRequest()

    @pytest.fixture
    def view(self):
        """Returns a DummyView instance with the mixin."""
        return TestCoordinatorSessionMixin.View()

    def test_user_is_not_coordinator_in_empty_session(self, view):  # noqa
        assert view.is_coordinator is False

    def test_user_is_coordinator_after_init(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        assert view.is_coordinator is True

    def test_orderid_is_set_after_init(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        assert view.coordinated_order_id == 1

    def test_user_is_not_coordinator_after_disable(self, view):  # noqa
        order = Order(id=1, coordinator='Hugo')
        view.enable_order_coordination(order)
        view.disable_order_coordination()
        assert view.is_coordinator is False
