# pylint: disable=C0111
from django.db import models


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

    def add_item(self, participant, description, price, amount):
        """Add a new item to this order."""
        item = OrderItem(
            order=self,
            participant=participant,
            description=description,
            price=price,
            amount=amount
        )
        item.save()


class OrderItem(models.Model):
    """
    Order items within an order for individual users.

    The same user may create multiple order items for different food.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    participant = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.PositiveIntegerField()


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
