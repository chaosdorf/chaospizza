# pylint: disable=C0111
"""All available endpoints of the chaospizza web project."""
from django.conf import settings
from django.conf.urls import include, re_path
from django.contrib import admin
from django.views import defaults as default_views


urlpatterns = [
    re_path(r'^', include('chaospizza.orders.urls')),
    re_path(r'^menus/', include('chaospizza.menus.urls')),
    re_path(r'^admin/', admin.site.urls, name='admin'),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        re_path(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        re_path(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
