# pylint: disable=R0903
"""Order module views."""


class UserSessionMixin:
    """Encapsulates actions on the current session's user."""

    @property
    def username(self):
        """Return the name of the current user, or None."""
        return self.request.session.get('username', None)

    @username.setter
    def username(self, value):
        self.request.session['username'] = value


class CoordinatorSessionMixin(UserSessionMixin):
    """Encapsulates actions on the current session's coordinator state."""

    def enable_order_coordination(self, order):
        """
        Enable order coordination for the current session.

        :param order: Order this user should coordinate.
        """
        self.request.session['is_coordinator'] = True
        self.request.session['order_id'] = order.id

    @property
    def is_coordinator(self):
        """Determine if the current user coordinates an order."""
        return self.request.session.get('is_coordinator', False)

    @property
    def coordinated_order_id(self):
        """Return the internal pk of the order record that the current user coordinates, or None."""
        return self.request.session.get('order_id', None)

    def disable_order_coordination(self):
        """Disable order coordination for the current session."""
        del self.request.session['is_coordinator']
        del self.request.session['order_id']


def user_request_context_processor(request):
    """Add user session information to the template context."""
    data = {
        'user': {
            'name': request.session.get('username', None),
            'is_coordinator': request.session.get('is_coordinator', None),
            'coordinated_order_id': request.session.get('order_id', None),
        }
    }
    print(data)
    return data
