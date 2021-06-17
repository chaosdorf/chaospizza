# pylint: disable=C0111
# pylint: disable=R0201
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

    def announce_order(self, coordinator=None, restaurant_name=None, restaurant_url=None):
        if not coordinator and not restaurant_name:
            return self.client.get(reverse('orders:create_order'))
        data = {
            'coordinator': coordinator,
            'restaurant_name': restaurant_name
        }
        if restaurant_url:
            data['restaurant_url'] = restaurant_url
        return self.client.post(
            reverse('orders:create_order'),
            data=data,
            follow=True
        )

    def update_order_state(self, order_slug, new_state=None):
        return self.client.post(
            reverse('orders:update_state', kwargs={'order_slug': order_slug}),
            data=None if new_state is None else {'new_state': new_state},
            follow=True
        )

    def cancel_order(self, order_slug, reason=None):
        return self.client.post(
            reverse('orders:cancel_order', kwargs={'order_slug': order_slug}),
            data=None if reason is None else {'reason': reason},
            follow=True
        )

    def add_order_item(self, order_slug, data=None):
        url = reverse('orders:create_orderitem', kwargs={'order_slug': order_slug})
        if not data:
            return self.client.get(url)
        return self.client.post(
            url,
            data=data,
            follow=True
        )

    def update_order_item(self, order_slug, item_slug, data=None):
        url = reverse('orders:update_orderitem', kwargs={'order_slug': order_slug, 'item_slug': item_slug})
        if not data:
            return self.client.get(url)
        return self.client.post(
            url,
            data=data,
            follow=True
        )

    def delete_order_item(self, order_slug, item_slug, get=False):
        url = reverse('orders:delete_orderitem', kwargs={'order_slug': order_slug, 'item_slug': item_slug})
        if get:
            return self.client.get(url)
        return self.client.post(
            url,
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
        assert order.slug is not None
        assert order.restaurant_name == 'Hallo Pizza'
        assert order.coordinator == 'Bernd'
        assert order.is_preparing is True

        user = view_order_response.context['chaospizza_user']
        assert user['name'] == 'Bernd'
        assert user['is_coordinator'] is True
        assert user['coordinated_order_slug'] == order.slug

    def test_order_is_listed_after_announcement(self, client):
        client.announce_order('Bernd', 'Hallo Pizza', 'https://www.hallopizza.de/')

        view_orders_response = client.list_orders()
        assert view_orders_response.status_code == 200

        orders = view_orders_response.context['order_list']
        user = view_orders_response.context['chaospizza_user']
        assert len(orders) == 1
        assert orders[0].slug == user['coordinated_order_slug']
        assert orders[0].coordinator == 'Bernd'
        assert orders[0].restaurant_name == 'Hallo Pizza'
        assert orders[0].restaurant_url == 'https://www.hallopizza.de/'
        assert orders[0].is_preparing is True

    def test_user_cannot_announce_multiple_orders(self, client):
        client.announce_order('Bernd', 'Hallo Pizza')

        view_orders_response = client.announce_order('Bernd', 'Pizza Hut')
        assert view_orders_response.status_code == 200
        assert len(view_orders_response.redirect_chain) == 1

        orders = view_orders_response.context['order_list']
        assert len(orders) == 1

    def test_username_is_pre_filled_when_a_second_order_is_announced(self, client):
        first_announce_response = client.announce_order('Bernd', 'Hallo Pizza')
        order_slug = first_announce_response.context['order'].slug
        client.update_order_state(order_slug, 'ordering')
        client.update_order_state(order_slug, 'ordered')
        client.update_order_state(order_slug, 'delivered')

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

    def test_order_state_change_requires_new_state_given(self, coordinator_client, coordinator_order):
        response = coordinator_client.update_order_state(coordinator_order.slug)
        assert response.context['order'].is_preparing is True

    def test_order_state_change_ignores_empty_new_state(self, coordinator_client, coordinator_order):
        response = coordinator_client.update_order_state(coordinator_order.slug, new_state='')
        assert response.context['order'].is_preparing is True

    def test_order_state_change_ignores_bogus_new_state(self, coordinator_client, coordinator_order):
        response = coordinator_client.update_order_state(coordinator_order.slug, new_state='ajksdfjksdf')
        assert response.context['order'].is_preparing is True

    def test_order_cancellation_requires_reason_given(self, coordinator_client, coordinator_order):
        response = coordinator_client.cancel_order(coordinator_order.slug)
        assert response.context['order'].is_canceled is False

    def test_order_cancellation_requires_non_empty_reason(self, coordinator_client, coordinator_order):
        response = coordinator_client.cancel_order(coordinator_order.slug, reason='')
        assert response.context['order'].is_canceled is False

    def test_coordinator_can_change_state_of_coordinated_order(self, coordinator_client, coordinator_order):
        response = coordinator_client.update_order_state(coordinator_order.slug, 'ordering')
        assert response.context['order'].is_ordering is True
        response = coordinator_client.update_order_state(coordinator_order.slug, 'ordered')
        assert response.context['order'].is_ordered is True
        response = coordinator_client.update_order_state(coordinator_order.slug, 'delivered')
        assert response.context['order'].is_delivered is True

    def test_coordinator_can_cancel_coordinated_order(self, coordinator_client, coordinator_order):
        response = coordinator_client.cancel_order(coordinator_order.slug, reason='Fuck off')
        assert response.context['order'].is_canceled is True

    def test_order_can_be_only_canceled_once(self, coordinator_client, coordinator_order):
        coordinator_client.cancel_order(coordinator_order.slug, reason='Fuck off')
        response = coordinator_client.cancel_order(coordinator_order.slug, reason='Fuck off')
        assert response.context['order'].is_canceled is True

    def test_coordinator_cannot_change_state_of_other_orders(self, coordinator_client, other_order):
        coordinator_client.announce_order('Bernd', 'Hallo Pizza')
        response = coordinator_client.update_order_state(other_order.slug, 'ordering')
        assert response.context['order'].is_ordering is False

    def test_coordinator_cannot_cancel_other_orders(self, coordinator_client, other_order):
        coordinator_client.announce_order('Bernd', 'Hallo Pizza')
        response = coordinator_client.cancel_order(other_order.slug, reason='Funpark ist tot')
        assert response.context['order'].is_canceled is False

    def test_anonymous_user_cannot_change_state_of_other_orders(self, anonymous_client, other_order):
        response = anonymous_client.update_order_state(other_order.slug, 'ordering')
        assert response.context['order'].is_ordering is False

    def test_anonymous_user_cannot_to_cancel_other_orders(self, anonymous_client, other_order):
        response = anonymous_client.cancel_order(other_order.slug, reason='Funpark ist tot')
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
        add_item_response = first_user_client.add_order_item(coordinator_order.slug, data={
            'participant': 'Mercedesfahrer-Bernd',
            'description': 'Abooooow',
            'price': '15.5',
            'amount': '1',
        })
        return add_item_response.context['order'].items.get()

    @pytest.fixture
    def second_user_client(self):
        return OrderClient(Client())

    @pytest.fixture
    def second_user_item(self, second_user_client, coordinator_order):
        add_item_response = second_user_client.add_order_item(coordinator_order.slug, data={
            'participant': 'Funpark-Bernd',
            'description': 'Pappen',
            'price': '15.5',
            'amount': '5',
        })
        return add_item_response.context['order'].items.get()

    @pytest.mark.django_db
    def test_add_order_item_shows_order_data(self, first_user_client, coordinator_order):
        response = first_user_client.add_order_item(coordinator_order.slug)
        assert response.context['order'].restaurant_name == coordinator_order.restaurant_name

    @pytest.mark.django_db
    def test_edit_order_item_shows_order_data(self, first_user_client, coordinator_order, first_user_item):
        response = first_user_client.update_order_item(coordinator_order.slug, first_user_item.slug)
        assert response.context['order'].restaurant_name == coordinator_order.restaurant_name

    @pytest.mark.django_db
    def test_delete_order_item_shows_order_data(self, first_user_client, coordinator_order, first_user_item):
        response = first_user_client.delete_order_item(coordinator_order.slug, first_user_item.slug, get=True)
        assert response.context['order'].restaurant_name == coordinator_order.restaurant_name

    @pytest.mark.django_db
    class TestWhenOrderIsPreparing:
        def test_user_can_add_item(self, first_user_client, coordinator_order):
            add_item_response = first_user_client.add_order_item(coordinator_order.slug, data={
                'participant': 'Mercedesfahrer-Bernd',
                'description': 'Abooooow',
                'price': '15.5',
                'amount': '1',
            })
            items = add_item_response.context['order'].items.all()
            assert len(items) == 1
            assert items[0].participant == 'Mercedesfahrer-Bernd'
            assert items[0].description == 'Abooooow'
            assert items[0].price == Decimal('15.5')
            assert items[0].amount == 1

        def test_user_can_edit_own_items(self, first_user_client, coordinator_order, first_user_item):
            update_item_response = first_user_client.update_order_item(
                coordinator_order.slug,
                first_user_item.slug,
                data={
                    'description': 'Ja ok',
                    'price': '5.5',
                    'amount': '10',
                }
            )
            items = list(update_item_response.context['order'].items.all())
            assert items[0].description == 'Ja ok'
            assert items[0].price == Decimal('5.5')
            assert items[0].amount == 10

        def test_user_cant_edit_other_items(self, first_user_client, coordinator_order, second_user_item):
            update_item_response = first_user_client.update_order_item(
                coordinator_order.slug,
                second_user_item.slug,
                data={
                    'description': 'yolo',
                    'price': '3.0',
                    'amount': '10'
                }
            )
            items = list(update_item_response.context['order'].items.all())
            assert items[0].participant == 'Funpark-Bernd'
            assert items[0].description == 'Pappen'
            assert items[0].price == Decimal('15.5')
            assert items[0].amount == 5

        def test_user_can_delete_own_items(self, first_user_client, coordinator_order, first_user_item):
            deleted_item_response = first_user_client.delete_order_item(coordinator_order.slug, first_user_item.slug)
            items = list(deleted_item_response.context['order'].items.all())
            assert len(items) == 0

        def test_user_cant_delete_other_items(self, first_user_client, coordinator_order, second_user_item):
            update_item_response = first_user_client.delete_order_item(coordinator_order.slug, second_user_item.slug)
            items = list(update_item_response.context['order'].items.all())
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
                    response = coordinator_client.cancel_order(coordinator_order.slug, reason='Fuck off')
                    break
                response = coordinator_client.update_order_state(coordinator_order.slug, state)
            return response

        def test_user_cant_add_item(self, coordinator_client, coordinator_order, states, first_user_client):
            self.switch_order_state(coordinator_client, coordinator_order, states)
            add_item_response = first_user_client.add_order_item(coordinator_order.slug, data={
                'participant': 'Mercedesfahrer-Bernd',
                'description': 'Abooooow',
                'price': '15.5',
                'amount': '1',
            })
            items = list(add_item_response.context['order'].items.all())
            assert len(items) == 0

        def test_user_cant_edit_own_item(self, coordinator_client, coordinator_order, states,
                                         first_user_client, first_user_item):
            self.switch_order_state(coordinator_client, coordinator_order, states)
            update_item_response = first_user_client.update_order_item(
                coordinator_order.slug,
                first_user_item.slug,
                data={
                    'description': 'Ja ok',
                    'price': '5.5',
                    'amount': '10',
                }
            )
            items = list(update_item_response.context['order'].items.all())
            assert items[0].description == 'Abooooow'
            assert items[0].price == Decimal('15.5')
            assert items[0].amount == 1

        def test_user_cant_edit_other_items(self, coordinator_client, coordinator_order, states,
                                            first_user_client, second_user_item):
            self.switch_order_state(coordinator_client, coordinator_order, states)
            update_item_response = first_user_client.update_order_item(
                coordinator_order.slug,
                second_user_item.slug,
                data={
                    'description': 'yolo',
                    'price': '3.0',
                    'amount': '10'
                }
            )
            items = list(update_item_response.context['order'].items.all())
            assert items[0].participant == 'Funpark-Bernd'
            assert items[0].description == 'Pappen'
            assert items[0].price == Decimal('15.5')
            assert items[0].amount == 5

        def test_user_cant_delete_own_item(self, coordinator_client, coordinator_order, states,
                                           first_user_client, first_user_item):
            self.switch_order_state(coordinator_client, coordinator_order, states)
            deleted_item_response = first_user_client.delete_order_item(coordinator_order.slug, first_user_item.slug)
            items = list(deleted_item_response.context['order'].items.all())
            assert len(items) == 1

        def test_user_cant_delete_other_items(self, coordinator_client, coordinator_order, states,
                                              first_user_client, second_user_item):
            self.switch_order_state(coordinator_client, coordinator_order, states)
            update_item_response = first_user_client.delete_order_item(coordinator_order.slug, second_user_item.slug)
            items = list(update_item_response.context['order'].items.all())
            assert len(items) == 1
