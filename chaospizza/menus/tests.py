# pylint: disable=C0111
# pylint: disable=R0201
from django.urls import reverse


def test_dummy_view(client):
    response = client.get(reverse('menu_home'))
    assert response.content == b'hi from menus app'
