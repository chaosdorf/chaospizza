# pylint: disable=C0111
# pylint: disable=R0201
# pylint: disable=W0201
# pylint: disable=W0613
from django import forms
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages

from ..models import Order, OrderItem
from ..mixins import UserSessionMixin


class CreateOrderItem(UserSessionMixin, CreateView):
    """Add a new order item to an existing order."""

    model = OrderItem
    fields = ['participant', 'description', 'price', 'amount']

    def get_initial(self):
        """Populate the participant name if the user is already known in the session."""
        return {'participant': self.username}

    def get_context_data(self, **kwargs):
        """Load associated Order record."""
        context = super(CreateOrderItem, self).get_context_data(**kwargs)
        context['order'] = Order.objects.filter(pk=self.kwargs['order_slug']).get()
        return context

    def form_valid(self, form):
        """Associate created OrderItem with existing Order and add the participant's name to the session state."""
        order = Order.objects.filter(pk=self.kwargs['order_slug']).get()
        try:
            order_item = form.save(commit=False)
            order.add_item(order_item.participant, order_item.description, order_item.price, order_item.amount)
            self.username = order_item.participant
        except ValueError as err:
            messages.add_message(self.request, messages.ERROR, 'Could not add order item: {}'.format(err))
        return redirect('orders:view_order', order_slug=self.kwargs['order_slug'])


class UpdateOrderItemForm(forms.ModelForm):
    """Custom ModelForm for OrderItem where the participant field can not be changed."""

    class Meta:  # noqa
        model = OrderItem
        fields = ['participant', 'description', 'price', 'amount']

    participant = forms.CharField(disabled=True)


class UpdateOrderItem(UpdateView):
    """Update a single order item."""

    model = OrderItem
    slug_field = 'id'
    slug_url_kwarg = 'item_slug'
    form_class = UpdateOrderItemForm

    # TODO check if order can be modified
    # TODO make sure user is allowed to edit

    def get_context_data(self, **kwargs):
        """Load associated Order record."""
        context = super(UpdateOrderItem, self).get_context_data(**kwargs)
        context['order'] = Order.objects.filter(pk=self.kwargs['order_slug']).get()
        return context

    def get_success_url(self):
        """Return order detail view."""
        return reverse('orders:view_order', kwargs={'order_slug': self.kwargs['order_slug']})


class DeleteOrderItem(DeleteView):
    """Delete a single order item."""

    model = OrderItem
    slug_field = 'id'
    slug_url_kwarg = 'item_slug'

    # TODO check if order can be modified
    # TODO make sure user is allowed to edit
    def get_context_data(self, **kwargs):
        """Load associated Order record."""
        context = super(DeleteOrderItem, self).get_context_data(**kwargs)
        context['order'] = Order.objects.filter(pk=self.kwargs['order_slug']).get()
        return context

    def get_success_url(self):
        """Return order detail view."""
        return reverse('orders:view_order', kwargs={'order_slug': self.kwargs['order_slug']})
