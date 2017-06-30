# pylint: disable=C0111
# pylint: disable=R0201
# pylint: disable=W0201
# pylint: disable=W0613
from django import forms
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.contrib import messages

from .models import Order, OrderItem


class CoordinatorSessionMixin:
    """Encapsulates actions on the current session's coordinator state."""

    def is_coordinator(self):
        """Determine if the current user coordinates an order."""
        return 'is_coordinator' in self.request.session and self.request.session['is_coordinator']

    def coordinated_order_id(self):
        """Return the internal pk of the order record that the current user coordinates, or None."""
        return self.request.session['order_id'] if 'order_id' in self.request.session else None

    def coordinator_name(self):
        """Return the name of the current coordinator, or None."""
        return self.request.session['coordinator_name'] if 'coordinator_name' in self.request.session else None

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
        return {'coordinator': self.coordinator_name()}

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


class CreateOrderItem(CreateView):
    """Add a new order item to an existing order."""

    model = OrderItem
    fields = ['participant', 'description', 'price', 'amount']

    def get_initial(self):
        """Populate the participant name if the user is already known in the session."""
        if 'coordinator_name' in self.request.session:
            participant_name = self.request.session['coordinator_name']
        elif 'participant_name' in self.request.session:
            participant_name = self.request.session['participant_name']
        else:
            participant_name = None
        return {
            'participant': participant_name
        }

    def get_context_data(self, **kwargs):
        """Load associated Order record."""
        context = super(CreateOrderItem, self).get_context_data(**kwargs)
        context['order'] = Order.objects.filter(pk=self.kwargs['order_slug']).get()
        return context

    def form_valid(self, form):
        """Associate created OrderItem with existing Order and add the participant's name to the session state."""
        self.object = form.save(commit=False)
        self.object.order = Order.objects.filter(pk=self.kwargs['order_slug']).get()
        self.object.save()
        self.request.session['participant'] = self.object.participant
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
