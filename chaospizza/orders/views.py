# pylint: disable=C0111
# pylint: disable=R0201
from django.views import View
from django.shortcuts import render


class ListOrders(View):
    """Show orders."""

    def get(self, request):
        """Show a list of all orders available."""
        # TODO:
        # - retrieve all orders from database, order by date created
        return render(request, template_name='orders/list.html')


class CreateOrder(View):
    """Create a new order."""

    def get(self, request):
        """Show create formular."""
        return render(request, template_name='orders/create.html')

    def post(self, request):
        """Create new Order."""
        pass


class ViewOrder(View):
    """Yolo."""

    def get(self, request):
        """Yolo."""
        return render(request, template_name='orders/view.html')
