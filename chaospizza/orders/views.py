# pylint: disable=C0111
# pylint: disable=R0201
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.contrib import messages

from .models import Order


class ListOrders(ListView):
    """Show orders."""

    model = Order
    queryset = Order.objects.all().order_by('-created_at')


class CreateOrder(CreateView):
    """Create a new order."""

    model = Order
    fields = ['coordinator', 'restaurant_name']
    template_name_suffix = '_create'

    def get(self, request, *args, **kwargs):
        """Enforce only one active order per user at a time."""
        if 'is_coordinator' in self.request.session and self.request.session['is_coordinator']:
            messages.add_message(request, messages.INFO, 'You are already coordinating an order.')
            return redirect(reverse('orders:list'))
        return super(CreateOrder, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """Enable coordinator mode in session when data is valid."""
        response = super(CreateOrder, self).form_valid(form)
        self.request.session['order_id'] = self.object.id
        self.request.session['name'] = self.object.coordinator
        self.request.session['is_coordinator'] = True
        return response


class ViewOrder(DetailView):
    """Show single order."""

    model = Order
    slug_field = 'id'
