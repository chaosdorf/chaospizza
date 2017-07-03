# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C0301
# pylint: disable=C1801
# pylint: disable=R0201
# pylint: disable=R0903
# pylint: disable=R0913
"""
Tests for the view logic.

Note:
Testing actual HTML output seems too much work and does not add much benefit in our case.

Thus, all tests defined here only test the interface of the view layer (URLs + parameters as input, context data as
output), but not the template rendering itself.
"""
from decimal import Decimal
import pytest

from django.urls import reverse
from django.test import Client


class OrderClient:  # noqa
    """Wrap a django test client instance and provide a simple high-level API to call views in the order app."""
    def __init__(self, client):
        self.client = client

    def list_orders(self):
        return self.client.get(reverse('orders:list_orders'))

    def announce_order(self, coordinator=None, restaurant_name=None):
        if not coordinator and not restaurant_name:
            return self.client.get(reverse('orders:create_order'))
        return self.client.post(
            reverse('orders:create_order'),
            data={'coordinator': coordinator, 'restaurant_name': restaurant_name},
            follow=True
        )

    def update_order_state(self, order_id, new_state):
        return self.client.post(
            reverse('orders:update_state', kwargs={'order_slug': order_id}),
            data={'new_state': new_state} if new_state else None,
            follow=True
        )

    def cancel_order(self, order_id, reason=None):
        return self.client.post(
            reverse('orders:cancel_order', kwargs={'order_slug': order_id}),
            data={'reason': reason} if reason else None,
            follow=True
        )

    def add_order_item(self, order_id, data=None):
        return self.client.post(
            reverse('orders:create_orderitem', kwargs={'order_slug': order_id}),
            data=data,
            follow=True
        )

    def update_order_item(self, order_id, item_id, data=None):
        return self.client.post(
            reverse('orders:update_orderitem', kwargs={'order_slug': order_id, 'item_slug': item_id}),
            data=data,
            follow=True
        )

    def delete_order_item(self, order_id, item_id):
        return self.client.post(
            reverse('orders:delete_orderitem', kwargs={'order_slug': order_id, 'item_slug': item_id}),
            follow=True
        )


@pytest.mark.django_db
class TestOrderAnnouncement:
    @pytest.fixture
    def client(self):
        return OrderClient(Client())

    def test_new_user_can_announce_order(self, client):
        view_order_response = client.announce_order('Bernd', 'Hallo Pizza')
        assert view_order_response.status_code == 200
        assert len(view_order_response.redirect_chain) == 1

        order = view_order_response.context['order']
        assert order.id is not None
        assert order.restaurant_name == 'Hallo Pizza'
        assert order.coordinator == 'Bernd'
        assert order.is_preparing is True

        user = view_order_response.context['user']
        assert user['name'] == 'Bernd'
        assert user['is_coordinator'] is True
        assert user['coordinated_order_id'] == order.id

    def test_order_is_listed_after_announcement(self, client):
        client.announce_order('Bernd', 'Hallo Pizza')

        view_orders_response = client.list_orders()
        assert view_orders_response.status_code == 200

        orders = view_orders_response.context['order_list']
        user = view_orders_response.context['user']
        assert len(orders) == 1
        assert orders[0].id == user['coordinated_order_id']
        assert orders[0].restaurant_name == 'Hallo Pizza'
        assert orders[0].coordinator == 'Bernd'
        assert orders[0].is_preparing is True

    def test_user_cannot_announce_multiple_orders(self, client):
        client.announce_order('Bernd', 'Hallo Pizza')

        view_orders_response = client.announce_order('Bernd', 'Hallo Pizza')
        assert view_orders_response.status_code == 200
        assert len(view_orders_response.redirect_chain) == 1

        orders = view_orders_response.context['order_list']
        assert len(orders) == 1

    def test_username_is_pre_filled_when_a_second_order_is_announced(self, client):
        first_announce_response = client.announce_order('Bernd', 'Hallo Pizza')
        order_id = first_announce_response.context['order'].id
        client.update_order_state(order_id, 'ordering')
        client.update_order_state(order_id, 'ordered')
        client.update_order_state(order_id, 'delivered')

        second_announce_response = client.announce_order()
        assert second_announce_response.status_code == 200
        assert second_announce_response.context['form'].initial['coordinator'] == 'Bernd'


@pytest.mark.django_db
class TestOrderCoordination:
    @pytest.fixture
    def anonymous_client(self):
        return OrderClient(Client())

    @pytest.fixture
    def coordinator_client(self):
        return OrderClient(Client())

    @pytest.fixture
    def coordinator_order(self, coordinator_client):
        announce_response = coordinator_client.announce_order('Bernd', 'Hallo Pizza')
        return announce_response.context['order']

    @pytest.fixture
    def other_client(self):
        return OrderClient(Client())

    @pytest.fixture
    def other_order(self, other_client):
        announce_response = other_client.announce_order('Funpark-Bernd', 'Pizza Hut')
        return announce_response.context['order']

    def test_coordinator_can_change_state_of_coordinated_order(self, coordinator_client, coordinator_order):
        response = coordinator_client.update_order_state(coordinator_order.id, 'ordering')
        assert response.context['order'].is_ordering is True
        response = coordinator_client.update_order_state(coordinator_order.id, 'ordered')
        assert response.context['order'].is_ordered is True
        response = coordinator_client.update_order_state(coordinator_order.id, 'delivered')
        assert response.context['order'].is_delivered is True

    def test_coordinator_can_cancel_coordinated_order(self, coordinator_client, coordinator_order):
        response = coordinator_client.cancel_order(coordinator_order.id, reason='Fuck off')
        assert response.context['order'].is_canceled is True

    def test_order_cancellation_requires_reason(self, coordinator_client, coordinator_order):
        response = coordinator_client.cancel_order(coordinator_order.id)
        assert response.context['order'].is_canceled is False

    def test_coordinator_cannot_change_state_of_other_orders(self, coordinator_client, other_order):
        coordinator_client.announce_order('Bernd', 'Hallo Pizza')
        response = coordinator_client.update_order_state(other_order.id, 'ordering')
        assert response.context['order'].is_ordering is False

    def test_coordinator_cannot_cancel_other_orders(self, coordinator_client, other_order):
        coordinator_client.announce_order('Bernd', 'Hallo Pizza')
        response = coordinator_client.cancel_order(other_order.id, reason='Funpark ist tot')
        assert response.context['order'].is_canceled is False

    def test_anonymous_user_cannot_change_state_of_other_orders(self, anonymous_client, other_order):
        response = anonymous_client.update_order_state(other_order.id, 'ordering')
        assert response.context['order'].is_ordering is False

    def test_anonymous_user_cannot_to_cancel_other_orders(self, anonymous_client, other_order):
        response = anonymous_client.cancel_order(other_order.id, reason='Funpark ist tot')
        assert response.context['order'].is_canceled is False


class TestOrderParticipation:
    @pytest.fixture
    def coordinator_client(self):
        return OrderClient(Client())

    @pytest.fixture
    def coordinator_order(self, coordinator_client):
        announce_response = coordinator_client.announce_order('Bernd', 'Hallo Pizza')
        return announce_response.context['order']

    @pytest.fixture
    def first_user_client(self):
        return OrderClient(Client())

    @pytest.fixture
    def first_user_item(self, first_user_client, coordinator_order):
        add_item_response = first_user_client.add_order_item(coordinator_order.id, data={
            'participant': 'Mercedesfahrer-Bernd',
            'description': 'Abooooow',
            'price': '15.5',
            'amount': '1',
        })
        return add_item_response.context['order'].items().get()

    @pytest.fixture
    def second_user_client(self):
        return OrderClient(Client())

    @pytest.fixture
    def second_user_item(self, second_user_client, coordinator_order):
        add_item_response = second_user_client.add_order_item(coordinator_order.id, data={
            'participant': 'Funpark-Bernd',
            'description': 'Pappen',
            'price': '15.5',
            'amount': '5',
        })
        return add_item_response.context['order'].items().get()

    @pytest.mark.django_db
    class TestWhenOrderIsPreparing:
        def test_user_can_add_item(self, first_user_client, coordinator_order):
            add_item_response = first_user_client.add_order_item(coordinator_order.id, data={
                'participant': 'Mercedesfahrer-Bernd',
                'description': 'Abooooow',
                'price': '15.5',
                'amount': '1',
            })
            items = add_item_response.context['order'].items().all()
            assert len(items) == 1
            assert items[0].participant == 'Mercedesfahrer-Bernd'
            assert items[0].description == 'Abooooow'
            assert items[0].price == Decimal('15.5')
            assert items[0].amount == 1

        def test_user_can_edit_own_items(self, first_user_client, coordinator_order, first_user_item):
            update_item_response = first_user_client.update_order_item(coordinator_order.id, first_user_item.id, data={
                'description': 'Ja ok',
                'price': '5.5',
                'amount': '10',
            })
            items = list(update_item_response.context['order'].items().all())
            assert items[0].description == 'Ja ok'
            assert items[0].price == Decimal('5.5')
            assert items[0].amount == 10

        def test_user_cant_edit_other_items(self, first_user_client, coordinator_order, second_user_item):
            update_item_response = first_user_client.update_order_item(coordinator_order.id, second_user_item.id, data={
                'description': 'yolo',
                'price': '3.0',
                'amount': '10'
            })
            items = list(update_item_response.context['order'].items().all())
            assert items[0].participant == 'Funpark-Bernd'
            assert items[0].description == 'Pappen'
            assert items[0].price == Decimal('15.5')
            assert items[0].amount == 5

        def test_user_can_delete_own_items(self, first_user_client, coordinator_order, first_user_item):
            deleted_item_response = first_user_client.delete_order_item(coordinator_order.id, first_user_item.id)
            items = list(deleted_item_response.context['order'].items().all())
            assert len(items) == 0

        def test_user_cant_delete_other_items(self, first_user_client, coordinator_order, second_user_item):
            update_item_response = first_user_client.delete_order_item(coordinator_order.id, second_user_item.id)
            items = list(update_item_response.context['order'].items().all())
            assert len(items) == 1

    @pytest.mark.django_db
    @pytest.mark.parametrize("states", [
        (['ordering']),
        (['ordering', 'ordered']),
        (['ordering', 'ordered', 'delivered']),
        (['canceled']),
    ])
    class TestAfterOrderIsPreparing:
        @staticmethod
        def switch_order_state(coordinator_client, coordinator_order, states):
            """
            Performs the given state changes for an existing order.

            :param coordinator_client: django test client instance
            :param coordinator_order:  existing order
            :param states: list of state changes which will be run in the given order
            :return: http response from django client
            """
            response = None
            for state in states:
                if state == 'canceled':
                    response = coordinator_client.cancel_order(coordinator_order.id, reason='Fuck off')
                    break
                response = coordinator_client.update_order_state(coordinator_order.id, state)
            return response

        def test_user_cant_add_item(self, coordinator_client, coordinator_order, states, first_user_client):
            self.switch_order_state(coordinator_client, coordinator_order, states)
            add_item_response = first_user_client.add_order_item(coordinator_order.id, data={
                'participant': 'Mercedesfahrer-Bernd',
                'description': 'Abooooow',
                'price': '15.5',
                'amount': '1',
            })
            items = list(add_item_response.context['order'].items().all())
            assert len(items) == 0

        def test_user_cant_edit_item(self, coordinator_client, coordinator_order, states,
                                     first_user_client, first_user_item):
            self.switch_order_state(coordinator_client, coordinator_order, states)
            update_item_response = first_user_client.update_order_item(coordinator_order.id, first_user_item.id, data={
                'description': 'Ja ok',
                'price': '5.5',
                'amount': '10',
            })
            items = list(update_item_response.context['order'].items().all())
            assert items[0].description == 'Abooooow'
            assert items[0].price == Decimal('15.5')
            assert items[0].amount == 1

        def test_user_cant_delete_item(self, coordinator_client, coordinator_order, states,
                                       first_user_client, first_user_item,):
            self.switch_order_state(coordinator_client, coordinator_order, states)
            deleted_item_response = first_user_client.delete_order_item(coordinator_order.id, first_user_item.id)
            items = list(deleted_item_response.context['order'].items().all())
            assert len(items) == 1
