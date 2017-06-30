# pylint: disable=C0111
# pylint: disable=R0201
# pylint: disable=W0201
# pylint: disable=W0613
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.contrib import messages

from . import CoordinatorSessionMixin
from ..models import Order


class ListOrders(ListView):
    """Show orders."""

    model = Order
    queryset = Order.objects.all().order_by('-created_at')


class CreateOrder(CoordinatorSessionMixin, CreateView):
    """Create a new order."""

    model = Order
    fields = ['coordinator', 'restaurant_name']
    template_name_suffix = '_create'

    def get_initial(self):
        """Populate the coordinator name if the user is already known in the session."""
        return {'coordinator': self.username}

    def get(self, request, *args, **kwargs):
        """Enforce only one active order per user at a time."""
        if self.is_coordinator:
            messages.add_message(request, messages.INFO, 'You are already coordinating an order.')
            return redirect(reverse('orders:list_orders'))
        return super(CreateOrder, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """Enable coordinator mode in session when data is valid."""
        response = super(CreateOrder, self).form_valid(form)
        self.username = self.object.coordinator
        self.enable_order_coordination(self.object)
        return response


class ViewOrder(CoordinatorSessionMixin, DetailView):
    """Show single order."""

    model = Order
    slug_field = 'id'
    slug_url_kwarg = 'order_slug'


class UpdateOrderState(SingleObjectMixin, CoordinatorSessionMixin, View):  # noqa
    """Update the state of a specific order."""

    model = Order
    slug_field = 'id'
    slug_url_kwarg = 'order_slug'

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        new_state = request.POST['new_state']
        order = self.get_object()
        if new_state == 'ordering':
            order.ordering()
            messages.add_message(request, messages.INFO, 'New state ordering')
        elif new_state == 'ordered':
            order.ordered()
            messages.add_message(request, messages.INFO, 'New state ordered')
        elif new_state == 'delivered':
            order.delivered()
            self.disable_order_coordination()
            messages.add_message(request, messages.INFO, 'Order finished.')
        else:
            messages.add_message(request, messages.ERROR, 'Not possible')
        return redirect(reverse('orders:view_order', kwargs={'order_slug': order.id}))


class CancelOrder(SingleObjectMixin, CoordinatorSessionMixin, View):
    """Cancel a specific order."""

    model = Order
    slug_field = 'id'
    slug_url_kwarg = 'order_slug'

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        reason = request.POST['reason']
        order = self.get_object()
        try:
            order.cancel(reason)
            self.disable_order_coordination()
            messages.add_message(request, messages.ERROR, 'Order #{} canceled'.format(order.id))
        except ValueError as err:
            messages.add_message(request, messages.ERROR, 'Order #{} could not be canceled: {}'.format(order.id, err))
        return redirect(reverse('orders:view_order', kwargs={'order_slug': order.id}))
