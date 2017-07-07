# pylint: disable=C0111
# https://github.com/PyCQA/pylint/issues/1553
# pylint: disable=W0221
from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


ORDER_STATES = (
    ('preparing', 'Order is prepared, order items can be modified.'),
    ('ordering', 'Order is locked and sent to delivery service by coordinator.'),
    ('ordered', 'Order has been sent to delivery service.'),
    ('delivered', 'Delivery has arrived.'),
    ('canceled', 'Order has been canceled due to some reason.'),
)


class Order(models.Model):
    """
    Represents an order which is used to help coordinate food delivery for multiple users.

    Users can add order items as they like when the state is preparing.
    """

    class Meta:  # noqa
        ordering = ('history__created_at', )
        unique_together = ('coordinator', 'restaurant_name')

    slug = models.SlugField(max_length=50)
    coordinator = models.CharField(max_length=100)
    restaurant_name = models.CharField(max_length=250)
    state = models.CharField(max_length=16, choices=ORDER_STATES, default='preparing')
    # TODO remove this and always generate from state changes?
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """Return public url to view single order."""
        return reverse('orders:view_order', kwargs={'order_slug': self.slug})

    def save(self, *args, **kwargs):
        """Generate order slug based on coordinator and restaurant name."""
        self.slug = slugify("{} {}".format(self.coordinator, self.restaurant_name))
        super(Order, self).save(*args, **kwargs)

    def __expect_states(self, expected_state):
        if self.state not in expected_state:
            raise ValueError("Need state '{}' but is '{}'".format(expected_state, self.state))

    def __update_state(self, new_state, reason=None):
        log_entry = OrderStateChange(
            order=self,
            old_state=self.state,
            new_state=new_state,
            reason=reason
        )
        self.state = new_state
        self.save()
        # TODO signal?
        log_entry.save()

    @property
    def is_preparing(self):
        """Return True if the order has state preparing."""
        return self.state == 'preparing'

    def ordering(self):
        """
        Set order state to ordering.

        Adding new items is not allowed afterwards.
        """
        self.__expect_states(['preparing'])
        self.__update_state('ordering')

    @property
    def is_ordering(self):
        """Return True if the order has state ordering."""
        return self.state == 'ordering'

    def ordered(self):
        """Set order state to ordered."""
        self.__expect_states(['ordering'])
        self.__update_state('ordered')

    @property
    def is_ordered(self):
        """Return True if the order has state ordered."""
        return self.state == 'ordered'

    def delivered(self):
        """Set order state to final state delivered."""
        self.__expect_states(['ordered'])
        self.__update_state('delivered')

    @property
    def is_delivered(self):
        """Return True if the order has state delivered."""
        return self.state == 'delivered'

    def cancel(self, reason):
        """Set order state to final state canceled."""
        if not reason:
            raise ValueError('need reason for cancellation')
        self.__expect_states(['preparing', 'ordering', 'ordered'])
        self.__update_state('canceled', reason)

    @property
    def is_canceled(self):
        """Return True if the order has state cancelled."""
        return self.state == 'canceled'

    @property
    def total_price(self):
        """Calculate total order price based on all order items."""
        return sum([record.total_price for record in self.items.all()])


class OrderItem(models.Model):
    """
    Order items within an order for individual users.

    The same user may create multiple order items for different food.
    """

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    participant = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        """Prevent record from being saved when associated order is not preparing."""
        if not self.order.is_preparing:
            raise ValueError('Can only save order item when order is preparing, but order is {}'.format(
                self.order.state))
        super(OrderItem, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent record from being delete when associated order is not preparing."""
        if not self.order.is_preparing:
            raise ValueError('Can only delete order item when order is preparing, but order is {}'.format(
                self.order.state))
        super(OrderItem, self).delete(*args, **kwargs)

    @property
    def total_price(self):
        """Calculate total price of this item."""
        return self.price * Decimal(self.amount)


class OrderStateChange(models.Model):
    """
    Created whenever the state of an Order instance has been changed.

    Contains the old state, new state and an optional reason.
    """

    order = models.ForeignKey(Order, related_name='history', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    old_state = models.CharField(max_length=16, choices=ORDER_STATES)
    new_state = models.CharField(max_length=16, choices=ORDER_STATES)
    reason = models.CharField(max_length=1000, null=True)
