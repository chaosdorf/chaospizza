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

    def add_order_to_session(self, order):
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

    def user_can_edit_order(self, order_id):
        """Determine if the current user is allowed to edit the given order."""
        return self.is_coordinator and self.request.session.get('order_id', -1) == order_id

    def remove_order_from_session(self):
        """Disable order coordination for the current session."""
        del self.request.session['is_coordinator']
        del self.request.session['order_id']

    def add_order_item_to_session(self, order_id, order_item_id):
        """Store the given order_id/order_item_id in the session so we know what we are allowed to edit."""
        order_ids = self.request.session.setdefault('order_ids', {})
        item_ids = order_ids.setdefault(order_id, [])
        item_ids.append(order_item_id)

    def user_can_edit_order_item(self, order_id, order_item_id):
        """Determine if the current user is allowed to edit the given order_id/order_item_id."""
        order_ids = self.request.session.setdefault('order_ids', {})
        item_ids = order_ids.setdefault(order_id, [])
        return order_item_id in item_ids
