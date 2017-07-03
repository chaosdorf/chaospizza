# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C1801
# pylint: disable=R0201
# pylint: disable=R0903
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


def announce_order(client, coordinator, restaurant_name):
    url = reverse('orders:create_order')
    return client.post(url, data={'coordinator': coordinator, 'restaurant_name': restaurant_name}, follow=True)


def update_order_state(client, order_id, new_state):
    url = reverse('orders:update_state', kwargs={'order_slug': order_id})
    return client.post(url, data={'new_state': new_state}, follow=True)


def cancel_order(client, order_id, reason):
    url = reverse('orders:cancel_order', kwargs={'order_slug': order_id})
    return client.post(url, data={'reason': reason}, follow=True)


def add_order_item(client, order_id, data=None):
    if data is None:
        data = {}
    return client.post(
        reverse('orders:create_orderitem', kwargs={'order_slug': order_id}),
        data=data,
        follow=True
    )


def update_order_item(client, order_id, item_id, data=None):
    return client.post(
        reverse('orders:update_orderitem', kwargs={'order_slug': order_id, 'item_slug': item_id}),
        data=data,
        follow=True
    )


def delete_order_item(client, order_id, item_id):
    return client.post(
        reverse('orders:delete_orderitem', kwargs={'order_slug': order_id, 'item_slug': item_id}),
        follow=True
    )


@pytest.mark.django_db
class TestOrderAnnouncement:
    def test_new_user_can_announce_order(self, client):
        view_order_response = announce_order(client, 'Bernd', 'Hallo Pizza')
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
        announce_order(client, 'Bernd', 'Hallo Pizza')

        view_orders_response = client.get(reverse('orders:list_orders'))
        assert view_orders_response.status_code == 200

        orders = view_orders_response.context['order_list']
        user = view_orders_response.context['user']
        assert len(orders) == 1
        assert orders[0].id == user['coordinated_order_id']
        assert orders[0].restaurant_name == 'Hallo Pizza'
        assert orders[0].coordinator == 'Bernd'
        assert orders[0].is_preparing is True

    def test_user_cannot_announce_multiple_orders(self, client):
        announce_order(client, 'Bernd', 'Hallo Pizza')

        view_orders_response = announce_order(client, 'Bernd', 'Hallo Pizza')
        assert view_orders_response.status_code == 200
        assert len(view_orders_response.redirect_chain) == 1

        orders = view_orders_response.context['order_list']
        assert len(orders) == 1

    def test_username_is_pre_filled_when_a_second_order_is_announced(self, client):
        first_announce_response = announce_order(client, 'Bernd', 'Hallo Pizza')
        order_id = first_announce_response.context['order'].id
        update_order_state(client, order_id, 'ordering')
        update_order_state(client, order_id, 'ordered')
        update_order_state(client, order_id, 'delivered')

        second_announce_response = client.get(reverse('orders:create_order'))
        assert second_announce_response.status_code == 200
        assert second_announce_response.context['form'].initial['coordinator'] == 'Bernd'


@pytest.mark.django_db
class TestOrderCoordination:
    @pytest.fixture
    def order_id(self, client):
        announce_response = announce_order(client, 'Bernd', 'Hallo Pizza')
        return announce_response.context['order'].id

    @pytest.fixture
    def order_id_from_funpark_bernd(self):
        from django.test import Client
        client = Client()
        announce_response = announce_order(client, 'Funpark-Bernd', 'Pizza Hut')
        return announce_response.context['order'].id

    def test_coordinator_can_change_state_of_coordinated_order(self, client, order_id):
        response = update_order_state(client, order_id, 'ordering')
        assert response.context['order'].is_ordering is True
        response = update_order_state(client, order_id, 'ordered')
        assert response.context['order'].is_ordered is True
        response = update_order_state(client, order_id, 'delivered')
        assert response.context['order'].is_delivered is True

    def test_coordinator_can_cancel_coordinated_order(self, client, order_id):
        response = cancel_order(client, order_id, reason='Fuck off')
        assert response.context['order'].is_canceled is True

    def test_order_cancellation_requires_reason(self, client, order_id):
        url = reverse('orders:cancel_order', kwargs={'order_slug': order_id})
        response = client.post(url, follow=True)
        # TODO assert error message?
        assert response.context['order'].is_canceled is False

    def test_coordinator_cannot_change_state_of_other_orders(self, client, order_id_from_funpark_bernd):
        announce_order(client, 'Bernd', 'Hallo Pizza')
        response = update_order_state(client, order_id_from_funpark_bernd, 'ordering')
        # TODO assert error message?
        assert response.context['order'].is_ordering is False

    def test_coordinator_cannot_cancel_other_orders(self, client, order_id_from_funpark_bernd):
        announce_order(client, 'Bernd', 'Hallo Pizza')
        response = cancel_order(client, order_id_from_funpark_bernd, reason='Funpark ist tot')
        # TODO assert error message?
        assert response.context['order'].is_canceled is False

    def test_anonymous_user_cannot_change_state_of_other_orders(self, client, order_id_from_funpark_bernd):
        response = update_order_state(client, order_id_from_funpark_bernd, 'ordering')
        # TODO assert error message?
        assert response.context['order'].is_ordering is False

    def test_anonymous_user_cannot_to_cancel_other_orders(self, client, order_id_from_funpark_bernd):
        response = cancel_order(client, order_id_from_funpark_bernd, reason='Funpark ist tot')
        # TODO assert error message?
        assert response.context['order'].is_canceled is False


@pytest.mark.django_db
class TestOrderParticipation:
    @pytest.fixture
    def mercedes_client(self):
        from django.test import Client
        return Client()

    @pytest.fixture
    def funpark_client(self):
        from django.test import Client
        return Client()

    @pytest.fixture
    def order_id(self, client):
        announce_response = announce_order(client, 'Bernd', 'Hallo Pizza')
        return announce_response.context['order'].id

    @pytest.fixture
    def mercedes_item_id(self, mercedes_client, order_id):
        add_item_response = add_order_item(mercedes_client, order_id, data={
            'participant': 'Mercedesfahrer-Bernd',
            'description': 'Abooooow',
            'price': '15.5',
            'amount': '1',
        })
        return add_item_response.context['order'].items().get().id

    @pytest.fixture
    def funpark_item_id(self, funpark_client, order_id):
        add_item_response = add_order_item(funpark_client, order_id, data={
            'participant': 'Funpark-Bernd',
            'description': 'Pappen',
            'price': '15.5',
            'amount': '5',
        })
        return add_item_response.context['order'].items().get().id

    def test_user_can_add_item_when_order_is_prepared(self, mercedes_client, order_id):
        add_item_response = add_order_item(mercedes_client, order_id, data={
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

    def test_user_can_edit_own_items_when_order_is_prepared(self, mercedes_client, order_id, mercedes_item_id):
        update_item_response = update_order_item(mercedes_client, order_id, mercedes_item_id, data={
            'description': 'Ja ok',
            'price': '5.5',
            'amount': '10',
        })
        items = list(update_item_response.context['order'].items().all())
        assert items[0].description == 'Ja ok'
        assert items[0].price == Decimal('5.5')
        assert items[0].amount == 10

    def test_user_can_delete_own_items_when_order_is_prepared(self, mercedes_client, order_id, mercedes_item_id):
        deleted_item_response = delete_order_item(mercedes_client, order_id, mercedes_item_id)
        items = list(deleted_item_response.context['order'].items().all())
        assert len(items) == 0

    def test_user_is_not_allowed_to_edit_other_items(self, mercedes_client, order_id, funpark_item_id):
        update_item_response = update_order_item(mercedes_client, order_id, funpark_item_id, data={
            'description': 'yolo',
            'price': '3.0',
            'amount': '10'
        })
        items = list(update_item_response.context['order'].items().all())
        assert items[0].participant == 'Funpark-Bernd'
        assert items[0].description == 'Pappen'
        assert items[0].price == Decimal('15.5')
        assert items[0].amount == 5

    def test_user_is_not_allowed_to_delete_other_items(self, mercedes_client, order_id, funpark_item_id):
        update_item_response = delete_order_item(mercedes_client, order_id, funpark_item_id)
        items = list(update_item_response.context['order'].items().all())
        assert len(items) == 1

    def test_user_is_not_allowed_to_add_item_after_order_is_prepared(self, client, mercedes_client, order_id):
        update_order_state(client, order_id, 'ordering')
        add_item_response = add_order_item(mercedes_client, order_id, data={
            'participant': 'Mercedesfahrer-Bernd',
            'description': 'Abooooow',
            'price': '15.5',
            'amount': '1',
        })
        items = list(add_item_response.context['order'].items().all())
        assert len(items) == 0
