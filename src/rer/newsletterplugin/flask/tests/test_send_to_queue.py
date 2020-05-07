# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield import RichTextValue
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.adapter.subscriptions import IChannelSubscriptions
from rer.newsletterplugin.flask.interfaces import (
    INewsletterPluginFlaskSettings,
)
from rer.newsletter.utils import NOK
from rer.newsletter.utils import OK
from rer.newsletterplugin.flask.testing import (
    RER_NEWSLETTERPLUGIN_FLASK_INTEGRATION_TESTING,
)
from zope.component import getMultiAdapter

import requests_mock
import unittest

QUEUE_URL = u'http://foo.bar'


class SendToQueueTest(unittest.TestCase):

    layer = RER_NEWSLETTERPLUGIN_FLASK_INTEGRATION_TESTING

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

        self.message = api.content.create(
            container=self.channel,
            type='Message',
            title=u'Newsletter Foo vol. 1',
            text=RichTextValue(u'This is the first message'),
        )
        api.content.transition(obj=self.message, transition='publish')

        self.adapter = getMultiAdapter(
            (self.channel, self.request), IChannelSender
        )

        api.portal.set_registry_record(
            'queue_endpoint',
            QUEUE_URL,
            interface=INewsletterPluginFlaskSettings,
        )

    @requests_mock.mock()
    def test_return_nok_if_queue_endpoint_not_set(self, m):
        m.post(QUEUE_URL, status_code=200)
        api.portal.set_registry_record(
            'queue_endpoint', u'', interface=INewsletterPluginFlaskSettings
        )

        res = self.adapter.sendMessage(self.message)
        self.assertEqual(res, NOK)
        self.assertFalse(m.called)

        api.portal.set_registry_record(
            'queue_endpoint',
            QUEUE_URL,
            interface=INewsletterPluginFlaskSettings,
        )

    @requests_mock.mock()
    def test_return_ok_and_call_backend_if_queue_endpoint_is_set(self, m):
        m.post(QUEUE_URL, status_code=200)

        res = self.adapter.sendMessage(self.message)
        self.assertEqual(res, OK)
        self.assertTrue(m.called)

    @requests_mock.mock()
    def test_call_endpoint_with_required_parameters(self, m):
        m.post(QUEUE_URL, status_code=200)

        self.adapter.sendMessage(self.message)
        history = m.request_history[0]
        parameters = history.json()

        self.assertIn('channel_url', parameters)
        self.assertIn('mfrom', parameters)
        self.assertIn('send_uid', parameters)
        self.assertIn('subject', parameters)
        self.assertIn('subscribers', parameters)
        self.assertIn('text', parameters)

    @requests_mock.mock()
    def test_call_endpoint_with_right_channel_url(self, m):
        m.post(QUEUE_URL, status_code=200)

        self.adapter.sendMessage(self.message)
        history = m.request_history[0]
        parameters = history.json()

        self.assertEqual(
            parameters['channel_url'], self.channel.absolute_url()
        )

    @requests_mock.mock()
    def test_call_endpoint_with_right_subject(self, m):
        m.post(QUEUE_URL, status_code=200)

        self.adapter.sendMessage(self.message)
        history = m.request_history[0]
        parameters = history.json()

        self.assertEqual(parameters['subject'], self.message.Title())

    @requests_mock.mock()
    def test_call_endpoint_with_right_mfrom(self, m):
        m.post(QUEUE_URL, status_code=200)

        self.adapter.sendMessage(self.message)
        history = m.request_history[0]
        parameters = history.json()
        self.assertEqual(parameters['mfrom'], None)

        self.channel.sender_email = 'foo@bar.it'
        self.adapter.sendMessage(self.message)
        history = m.request_history[1]
        parameters = history.json()
        self.assertEqual(parameters['mfrom'], 'foo@bar.it')

        self.channel.sender_name = 'John Doe'
        self.adapter.sendMessage(self.message)
        history = m.request_history[2]
        parameters = history.json()
        self.assertEqual(parameters['mfrom'], 'John Doe <foo@bar.it>')

    @requests_mock.mock()
    def test_call_endpoint_with_right_subscribers_list(self, m):
        m.post(QUEUE_URL, status_code=200)

        self.adapter.sendMessage(self.message)
        history = m.request_history[0]
        parameters = history.json()
        self.assertEqual(parameters['subscribers'], [])

        subscribers_adapter = getMultiAdapter(
            (self.channel, self.request), IChannelSubscriptions
        )
        subscribers_adapter.addUser('foo@foo.com')
        self.adapter.sendMessage(self.message)
        history = m.request_history[1]
        parameters = history.json()
        self.assertEqual(parameters['subscribers'], ['foo@foo.com'])

    @requests_mock.mock()
    def test_call_endpoint_with_right_text(self, m):
        m.post(QUEUE_URL, status_code=200)

        self.adapter.sendMessage(self.message)
        history = m.request_history[0]
        parameters = history.json()
        self.assertIn(self.message.text.output, parameters['text'])
