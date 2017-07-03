# pylint: disable=C0111
# pylint: disable=R0201
# pylint: disable=W0201
# pylint: disable=W0613
# pylint: disable=E0602
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.contrib import messages

from ..mixins import UserSessionMixin
from ..models import Order


class ListOrders(ListView):
    """Show orders."""

    model = Order
    queryset = Order.objects.all().order_by('-created_at')


class CreateOrder(UserSessionMixin, CreateView):
    """Create a new order."""

    model = Order
    fields = ['coordinator', 'restaurant_name']
    template_name_suffix = '_create'

    def dispatch(self, request, *args, **kwargs):
        """Enforce only one active order per user at a time."""
        if self.is_coordinator:
            messages.add_message(request, messages.INFO, 'You are already coordinating an order.')
            return redirect(reverse('orders:list_orders'))
        return super(CreateOrder, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Populate the coordinator name if the user is already known in the session."""
        return {'coordinator': self.username}

    def form_valid(self, form):
        """Enable coordinator mode in session when data is valid."""
        response = super(CreateOrder, self).form_valid(form)
        self.register_for_coordination(self.object)
        return response

    def register_for_coordination(self, order):
        """Set coordinator mode for the current user and given order."""
        self.username = order.coordinator
        self.add_order_to_session(order)


class ViewOrder(UserSessionMixin, DetailView):
    """Show single order."""

    queryset = Order.objects.prefetch_related('items', 'history')
    slug_field = 'id'
    slug_url_kwarg = 'order_slug'


class UpdateOrderState(SingleObjectMixin, UserSessionMixin, View):
    """Update the state of a specific order."""

    model = Order
    slug_field = 'id'
    slug_url_kwarg = 'order_slug'

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        self.order = self.get_object()
        if self.user_can_edit_order(self.order.id):
            new_state = request.POST['new_state']
            self.update_order_state(request, new_state)
        else:
            messages.add_message(request, messages.ERROR, 'Operation not allowed.')
        return redirect(self.get_success_url())

    def update_order_state(self, request, new_state):
        """
        Try to set order's state and add a result message to the session.

        :param request: django http request
        :param new_state: either 'ordering', 'ordered' or 'delivered'
        """
        if new_state == 'ordering':
            self.order.ordering()
            messages.add_message(request, messages.INFO, 'New state ordering')
        elif new_state == 'ordered':
            self.order.ordered()
            messages.add_message(request, messages.INFO, 'New state ordered')
        elif new_state == 'delivered':
            self.order.delivered()
            self.remove_order_from_session()
            messages.add_message(request, messages.INFO, 'Order finished.')
        else:
            messages.add_message(request, messages.ERROR, 'Not possible')

    def get_success_url(self):
        """Return the view_order url for the current order."""
        return reverse('orders:view_order', kwargs={'order_slug': self.order.id})


class CancelOrder(SingleObjectMixin, UserSessionMixin, View):
    """Cancel a specific order."""

    model = Order
    slug_field = 'id'
    slug_url_kwarg = 'order_slug'

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        self.order = self.get_object()
        if self.user_can_edit_order(self.order.id):
            try:
                reason = request.POST['reason']
                self.cancel_order(request, reason)
            except KeyError:
                messages.add_message(request, messages.ERROR, 'Need reason to cancel order.')
        else:
            messages.add_message(request, messages.ERROR, 'Operation not allowed.')
        return redirect(self.get_success_url())

    def cancel_order(self, request, reason):
        """
        Try to cancel the order.

        :param request: django http request
        :param reason: why the order is canceled
        """
        try:
            self.order.cancel(reason)
            self.remove_order_from_session()
            messages.add_message(
                request, messages.ERROR,
                'Order #{} canceled'.format(self.order.id)
            )
        except ValueError as err:
            messages.add_message(
                request, messages.ERROR,
                'Order #{} could not be canceled: {}'.format(self.order.id, err)
            )

    def get_success_url(self):
        """Return the view_order url for the current order."""
        return reverse('orders:view_order', kwargs={'order_slug': self.order.id})
