# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=R0201
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
        assert 'user' in context
        assert context['user']['name'] is None
        assert context['user']['is_coordinator'] is False
        assert context['user']['coordinated_order_id'] is None

    def test_session_state_is_retrieved_correctly_for_participating_user(self):
        view = TestUserSessionContextProcessor.View()
        view.username = 'Detlef'
        context = user_session(view.request)
        assert 'user' in context
        assert context['user']['name'] == 'Detlef'
        assert context['user']['is_coordinator'] is False
        assert context['user']['coordinated_order_id'] is None

    def test_session_state_is_retrieved_correctly_for_coordinating_user(self):
        view = TestUserSessionContextProcessor.View()
        view.username = 'Hugo'
        view.add_order_to_session(Order(id=1, coordinator='Hugo'))
        context = user_session(view.request)
        assert 'user' in context
        assert context['user']['name'] == 'Hugo'
        assert context['user']['is_coordinator'] is True
        assert context['user']['coordinated_order_id'] == 1
