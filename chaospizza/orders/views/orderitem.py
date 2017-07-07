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

    def dispatch(self, request, *args, **kwargs):
        """Ensure that the associated order's state is preparing."""
        self.order = Order.objects.filter(slug=kwargs['order_slug']).get()
        if not self.order.is_preparing:
            messages.add_message(
                request, messages.ERROR,
                'Can not add order item, order is in state {}'.format(self.order.state)
            )
            return redirect('orders:view_order', order_slug=self.order.slug)
        return super(CreateOrderItem, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Populate the participant name if the user is already known in the session."""
        return {'participant': self.username}

    def get_context_data(self, **kwargs):
        """Load associated Order record."""
        context = super(CreateOrderItem, self).get_context_data(**kwargs)
        context['order'] = self.order
        return context

    def form_valid(self, form):
        """Associate created OrderItem with existing Order and add the participant's name to the session state."""
        form_order_item = form.save(commit=False)
        order_item = self.order.items.create(
            participant=form_order_item.participant,
            description=form_order_item.description,
            price=form_order_item.price,
            amount=form_order_item.amount,
        )
        self.add_order_item_to_session(str(self.order.id), str(order_item.id))
        self.username = order_item.participant
        return redirect('orders:view_order', order_slug=self.order.slug)


class UpdateOrderItemForm(forms.ModelForm):
    """Custom ModelForm for OrderItem where the participant field can not be changed."""

    class Meta:  # noqa
        model = OrderItem
        fields = ['participant', 'description', 'price', 'amount']

    participant = forms.CharField(disabled=True)


class UpdateOrderItem(UserSessionMixin, UpdateView):
    """Update a single order item."""

    model = OrderItem
    slug_field = 'id'
    slug_url_kwarg = 'item_slug'
    form_class = UpdateOrderItemForm

    def dispatch(self, request, *args, **kwargs):
        """Ensure that the associated order's state is preparing."""
        self.order = Order.objects.filter(slug=kwargs['order_slug']).get()
        if not self.order.is_preparing:
            messages.add_message(
                request, messages.ERROR,
                'Can not edit order item, order is in state {}'.format(self.order.state)
            )
            return redirect(self.get_success_url())
        if not self.user_can_edit_order_item(str(self.order.id), kwargs['item_slug']):
            messages.add_message(
                request, messages.ERROR,
                'Not allowed to edit order item.'
            )
            return redirect(self.get_success_url())
        return super(UpdateOrderItem, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Load associated Order record."""
        context = super(UpdateOrderItem, self).get_context_data(**kwargs)
        context['order'] = self.order
        return context

    def get_success_url(self):
        """Return order detail view."""
        return reverse('orders:view_order', kwargs={'order_slug': self.order.slug})


class DeleteOrderItem(UserSessionMixin, DeleteView):
    """Delete a single order item."""

    model = OrderItem
    slug_field = 'id'
    slug_url_kwarg = 'item_slug'

    def dispatch(self, request, *args, **kwargs):
        """Ensure that the associated order's state is preparing."""
        self.order = Order.objects.filter(slug=kwargs['order_slug']).get()
        if not self.order.is_preparing:
            messages.add_message(
                request, messages.ERROR,
                'Can not delete order item, order is in state {}'.format(self.order.state)
            )
            return redirect(self.get_success_url())
        if not self.user_can_edit_order_item(str(self.order.id), kwargs['item_slug']):
            messages.add_message(
                request, messages.ERROR,
                'Not allowed to delete order item.'
            )
            return redirect(self.get_success_url())
        return super(DeleteOrderItem, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Load associated Order record."""
        context = super(DeleteOrderItem, self).get_context_data(**kwargs)
        context['order'] = self.order
        return context

    def get_success_url(self):
        """Return order detail view."""
        return reverse('orders:view_order', kwargs={'order_slug': self.order.slug})
