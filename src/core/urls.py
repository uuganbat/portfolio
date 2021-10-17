#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importlib import import_module

from django.conf import settings
from django.conf.urls import patterns, url
from django import template
from django.utils.log import getLogger

from core import Nurl

rawurlpatterns = patterns('')

# Import if ROOT urls.py exists if not ignore it
try:
    rawurlpatterns += import_module('urls').urlpatterns
except ImportError as ex:
    pass #ignore it

# Import installed app urls
for app in settings.INSTALLED_APPS:
    if app.startswith('app.'):
        try:
            rawurlpatterns += import_module('%s.urls' % app).urlpatterns
        except ImportError as ex:
            getLogger('app').error('[import urls] app: %s, error: %s' % (app, str(ex)))

urlpatterns = patterns('')

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        url(r'^404/$', 'core.views.handler404'),
        url(r'^500/$', 'core.views.handler500'),
    )


if settings.DEBUG and hasattr(settings, 'APP_URL_PREFIX') and settings.APP_URL_PREFIX:
    for entry in rawurlpatterns:
        urlpatterns += patterns('',
            Nurl(r'^%s/%s' % (settings.APP_URL_PREFIX, entry.regex.pattern.replace('^',''))) > '%s.%s' % (entry.callback.__module__, entry.callback.__name__),
        )
else:
    urlpatterns = rawurlpatterns

template.add_to_builtins('core.template_tags.common')
template.add_to_builtins('core.template_tags.ajax')
template.add_to_builtins('core.template_tags.assets')
template.add_to_builtins('core.template_tags.pagination')
template.add_to_builtins('core.template_tags.bootstrap3')
template.add_to_builtins('core.template_tags.set_variable')
template.add_to_builtins('core.template_tags.mathfilters')

handler500 = 'core.views.handler500'
handler404 = 'core.views.handler404'
