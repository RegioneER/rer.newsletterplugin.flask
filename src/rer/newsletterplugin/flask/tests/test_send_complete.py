# -*- coding: utf-8 -*-
from persistent.dict import PersistentDict
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.adapter.sender import HISTORY_KEY
from rer.newsletterplugin.flask.testing import (
    RER_NEWSLETTERPLUGIN_FLASK_API_FUNCTIONAL_TESTING,
)
from zope.component import getMultiAdapter

import unittest
import transaction


class SendCompleteServiceTest(unittest.TestCase):

    layer = RER_NEWSLETTERPLUGIN_FLASK_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.channel = api.content.create(
            container=self.portal,
            type='Channel',
            title='Example channel',
            is_subscribable=True,
        )
        self.channel_url = self.channel.absolute_url()
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_reply_with_error_if_required_fields_not_passed(self):
        payload = {}
        response = self.api_session.post(
            '{}/@send-complete'.format(self.channel_url), json=payload
        )
        self.assertEqual(response.status_code, 400)

    def test_reply_with_error_if_id_is_invalid(self):
        payload = {'send_uid': 'foo'}
        response = self.api_session.post(
            '{}/@send-complete'.format(self.channel_url), json=payload
        )
        self.assertEqual(response.status_code, 500)

    def test_update_end_date_if_is_right_uid(self):
        adapter = getMultiAdapter((self.channel, self.request), IChannelSender)
        history = adapter.get_annotations_for_channel(key=HISTORY_KEY)
        history.append(PersistentDict({'uid': 'foo'}))
        transaction.commit()

        payload = {'send_uid': 'foo'}
        response = self.api_session.post(
            '{}/@send-complete'.format(self.channel_url), json=payload
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertNotEqual(history[0]['send_date_end'], '---')
        self.assertTrue(history[0]['completed'])

    def test_mark_not_complete_if_pass_error_flag(self):
        adapter = getMultiAdapter((self.channel, self.request), IChannelSender)
        history = adapter.get_annotations_for_channel(key=HISTORY_KEY)
        history.append(PersistentDict({'uid': 'foo'}))
        transaction.commit()

        payload = {'send_uid': 'foo', 'error': True}
        response = self.api_session.post(
            '{}/@send-complete'.format(self.channel_url), json=payload
        )
        transaction.commit()
        self.assertEqual(response.status_code, 204)
        self.assertNotEqual(history[0]['send_date_end'], '---')
        self.assertFalse(history[0]['completed'])
