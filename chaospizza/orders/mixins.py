# pylint: disable=C0111
class UserSessionMixin:
    """View mixin to retrieve and manipulate order-related session state."""

    @property
    def username(self):
        """Return the name of the current user, or None."""
        return self.request.session.get('username', None)

    @username.setter
    def username(self, value):
        self.request.session['username'] = value

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
