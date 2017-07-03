# pylint: disable=C0111
from decimal import Decimal
from django.db import models
from django.urls import reverse


ORDER_STATES = (
    ('preparing', ''),
    ('ordering', ''),
    ('ordered', ''),
    ('delivered', ''),
    ('canceled', ''),
)


class Order(models.Model):
    """
    Represents an order which is used to help coordinate food delivery for multiple users.

    Users can add order items as they like when the state is preparing.
    """

    coordinator = models.CharField(max_length=100)
    restaurant_name = models.CharField(max_length=250)
    state = models.CharField(max_length=16, choices=ORDER_STATES, default='preparing')
    # TODO remove this and always generate from state changes?
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """Return public url to view single order."""
        return reverse('orders:view_order', kwargs={'order_slug': self.pk})

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

    def add_item(self, participant, description, price, amount):
        """Add a new item to this order."""
        if self.state != 'preparing':
            raise ValueError('Can not add new items when in state {}'.format(self.state))
        item = OrderItem(
            order=self,
            participant=participant,
            description=description,
            price=price,
            amount=amount
        )
        item.save()
        return item

    def items(self):
        """
        Return a QuerySet to find all OrderItem records associated with this particular Order record.

        The QuerySet created is not yet evaluated and can be amended further by the caller.
        """
        return OrderItem.objects.filter(order=self)

    def total_price(self):
        """Calculate total order price based on all order items."""
        return self.items()\
            .annotate(item_price=models.F('price') * models.F('amount'))\
            .aggregate(models.Sum('item_price', output_field=models.DecimalField()))['item_price__sum']

    def history(self):
        """
        Return a QuerySet to find all OrderStateChange records associated with this particular Order record.

        The QuerySet created is not yet evaluated and can be amended further by the caller. Records are sorted by
        creation date, newest record first.
        """
        return OrderStateChange.objects.filter(order=self).order_by('-created_at')


class OrderItem(models.Model):
    """
    Order items within an order for individual users.

    The same user may create multiple order items for different food.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    participant = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.PositiveIntegerField(default=1)

    def total_price(self):
        """Calculate total price of this item."""
        return self.price * Decimal(self.amount)


class OrderStateChange(models.Model):
    """
    Created whenever the state of an Order instance has been changed.

    Contains the old state, new state and an optional reason.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    old_state = models.CharField(max_length=16, choices=ORDER_STATES)
    new_state = models.CharField(max_length=16, choices=ORDER_STATES)
    reason = models.CharField(max_length=1000, null=True)
