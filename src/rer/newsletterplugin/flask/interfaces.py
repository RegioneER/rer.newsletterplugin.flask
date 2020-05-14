# -*- coding: utf-8 -*-
from plone import schema
from rer.newsletterplugin.flask import _
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IRerNewsletterpluginFlaskLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class INewsletterPluginFlaskSettings(Interface):
    """ Plugin settings"""

    queue_endpoint = schema.TextLine(
        title=_(u'queue_endpoint_label', default=u'Queue endpoint'),
        description=_(
            u'queue_endpoint_help',
            default=u'Insert the url of the Flask server that will handle the'
            u' queue (for example: http://127.0.0.1:5000/add-to-queue).',
        ),
        default=u'http://127.0.0.1:5000/add-to-queue',
        required=True,
    )
