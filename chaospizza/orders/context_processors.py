# pylint: disable=C0111
def user_session(request):
    """Add user session information to the template context."""
    return {
        'chaospizza_user': {
            'name': request.session.get('username', None),
            'is_coordinator': request.session.get('is_coordinator', False),
            'coordinated_order_id': request.session.get('order_id', None),
        }
    }
