# pylint: disable=C0111
# pylint: disable=R0903
from ..models import Order
from ..mixins import UserSessionMixin
from ..context_processors import user_session


class TestUserSessionContextProcessor:
    class Request:
        def __init__(self):
            self.session = {}

    class View(UserSessionMixin):
        def __init__(self):
            self.request = TestUserSessionContextProcessor.Request()

    def test_session_state_is_retrieved_correctly_for_anonymous_user(self):
        view = TestUserSessionContextProcessor.View()
        context = user_session(view.request)
        assert 'chaospizza_user' in context
        assert context['chaospizza_user']['name'] is None
        assert context['chaospizza_user']['is_coordinator'] is False
        assert context['chaospizza_user']['coordinated_order_slug'] is None

    def test_session_state_is_retrieved_correctly_for_participating_user(self):
        view = TestUserSessionContextProcessor.View()
        view.username = 'Detlef'
        context = user_session(view.request)
        assert 'chaospizza_user' in context
        assert context['chaospizza_user']['name'] == 'Detlef'
        assert context['chaospizza_user']['is_coordinator'] is False
        assert context['chaospizza_user']['coordinated_order_slug'] is None

    def test_session_state_is_retrieved_correctly_for_coordinating_user(self):
        view = TestUserSessionContextProcessor.View()
        view.username = 'Hugo'
        view.add_order_to_session(Order(coordinator='Hugo', restaurant_name='Hallo Pizza', slug='hugo-hallo-pizza'))
        context = user_session(view.request)
        assert 'chaospizza_user' in context
        assert context['chaospizza_user']['name'] == 'Hugo'
        assert context['chaospizza_user']['is_coordinator'] is True
        assert context['chaospizza_user']['coordinated_order_slug'] == 'hugo-hallo-pizza'
