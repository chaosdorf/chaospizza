# pylint: disable=C0111
# pylint: disable=R0201
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.contrib import messages

from .models import Order


class CoordinatorSessionMixin:
    """Encapsulates actions on the current session's coordinator state."""

    def is_coordinator(self):
        """Determine if the current user coordinates an order."""
        return 'is_coordinator' in self.request.session and self.request.session['is_coordinator']

    def enable_order_coordination(self, order):
        """
        Enable order coordination for the current session.

        :param order: Order this user should coordinate.
        """
        self.request.session['is_coordinator'] = True
        self.request.session['order_id'] = order.id
        self.request.session['coordinator_name'] = order.coordinator

    def disable_order_coordination(self):
        """Disable order coordination for the current session."""
        del self.request.session['is_coordinator']
        del self.request.session['order_id']
        del self.request.session['coordinator_name']


class ListOrders(ListView):
    """Show orders."""

    model = Order
    queryset = Order.objects.all().order_by('-created_at')


class CreateOrder(CoordinatorSessionMixin, CreateView):
    """Create a new order."""

    model = Order
    fields = ['coordinator', 'restaurant_name']
    template_name_suffix = '_create'

    def get(self, request, *args, **kwargs):
        """Enforce only one active order per user at a time."""
        if self.is_coordinator():
            messages.add_message(request, messages.INFO, 'You are already coordinating an order.')
            return redirect(reverse('orders:list_orders'))
        return super(CreateOrder, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """Enable coordinator mode in session when data is valid."""
        response = super(CreateOrder, self).form_valid(form)
        self.enable_order_coordination(self.object)
        return response


class ViewOrder(DetailView):
    """Show single order."""

    model = Order
    slug_field = 'id'
    slug_url_kwarg = 'order_slug'
