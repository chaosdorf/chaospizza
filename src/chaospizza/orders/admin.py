# pylint: disable=C0111
from django.contrib import admin
from .models import Order, OrderItem, OrderStateChange


class OrderItemInline(admin.TabularInline):  # noqa
    model = OrderItem


class OrderStateChangeInline(admin.TabularInline):  # noqa
    model = OrderStateChange


class OrderAdmin(admin.ModelAdmin):  # noqa
    list_fields = ('coordinator', 'restaurant_name')
    inlines = [
        OrderItemInline,
        OrderStateChangeInline,
    ]


admin.site.register(Order, OrderAdmin)
