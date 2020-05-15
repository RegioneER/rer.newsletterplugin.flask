# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.browser.settings import ISettingsSchema
from rer.newsletterplugin.flask.interfaces import (
    INewsletterPluginFlaskSettings,
)
from rer.newsletterplugin.flask.testing import (
    RER_NEWSLETTERPLUGIN_FLASK_FUNCTIONAL_TESTING,
)
from zope.component import getMultiAdapter

import unittest
import transaction

QUEUE_URL = u'http://foo.bar'


class SendToQueueTest(unittest.TestCase):

    layer = RER_NEWSLETTERPLUGIN_FLASK_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.channel = api.content.create(
            container=self.portal,
            type='Channel',
            title=u'Example channel',
            is_subscribable=True,
        )

        self.adapter = getMultiAdapter(
            (self.channel, self.request), IChannelSender
        )

        api.portal.set_registry_record(
            'queue_endpoint',
            QUEUE_URL,
            interface=INewsletterPluginFlaskSettings,
        )

    def test_do_not_convert_channel_url_if_converters_not_set(self):

        url = 'http://foo.com/example/bar'

        self.assertEqual(url, self.adapter.convert_url(url))

    def test_do_not_convert_channel_url_if_both_converters_are_not_set(self):

        url = 'http://foo.com/example/bar'
        api.portal.set_registry_record(
            'source_link', u'http://foo.com', ISettingsSchema
        )
        transaction.commit()

        self.assertEqual(url, self.adapter.convert_url(url))

        api.portal.set_registry_record('source_link', u'', ISettingsSchema)
        api.portal.set_registry_record(
            'destination_link', u'http://baz.com', ISettingsSchema
        )
        transaction.commit()

        self.assertEqual(url, self.adapter.convert_url(url))

    def test_convert_channel_url_if_both_converters_are_set(self):

        url = 'http://foo.com/example/bar'
        api.portal.set_registry_record(
            'source_link', u'http://foo.com', ISettingsSchema
        )
        api.portal.set_registry_record(
            'destination_link', u'http://baz.com', ISettingsSchema
        )
        transaction.commit()

        self.assertNotEqual(url, self.adapter.convert_url(url))
        self.assertEqual(
            'http://baz.com/example/bar', self.adapter.convert_url(url)
        )
