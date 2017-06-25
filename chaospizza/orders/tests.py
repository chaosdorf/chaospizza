# pylint: disable=C0111
# pylint: disable=R0201
import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_my_user():
    """Test basic SQL query."""
    try:
        me_user = User.objects.get(username='me')
        assert me_user.is_superuser
    except User.DoesNotExist:
        assert True
