# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from email.utils import formataddr
from plone import api
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.adapter.base_adapter import BaseAdapter
from rer.newsletter.adapter.base_adapter import IChannelSender
from rer.newsletter.utility.channel import INVALID_CHANNEL
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
from smtplib import SMTPRecipientsRefused
from zope.interface import implementer

import json
import requests

KEY = 'rer.newsletter.subscribers'


@implementer(IChannelSender)
class FlaskAdapter(BaseAdapter):
    """ Adapter per l'invio delle newsletter fuori da
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def sendMessage(self, channel, message, unsubscribe_footer=None):
        logger.debug('adapter: sendMessage %s %s', channel, message.title)

        flask_url = "http://127.0.0.1:5000/add-to-queue"

        headers = {"Content-Type": "application/json"}
        payload = {
                'channel_url': 'http://foo.com',
                'subscribers': ['foo', 'bar'],
                'subject': 'subject',
                'mfrom': 'foo@bar.com',
                '_authenticator': 'asdfghjkl',
                'text': '...',
            }

        response = requests.post(
            flask_url,
            data=json.dumps(payload),
            headers=headers,
        )

        if response.status_code != 200:
            logger.error(
                "adapter: can't sendMessage %s %s",
                channel,
                message.title
            )
            return UNHANDLED

        # nl = self._api(channel)
        # annotations, channel_obj = self._storage(channel)
        # if annotations is None:
        #     return INVALID_CHANNEL
        #
        # # costruisco il messaggio
        # body = self._getMessage(nl, message, unsubscribe_footer)
        #
        # nl_subject = ' - ' + nl.subject_email if nl.subject_email else u''
        # subject = message.title + nl_subject
        #
        # # costruisco l'indirizzo del mittente
        # sender = formataddr((nl.sender_name, nl.sender_name))
        #
        # # invio la mail ad ogni utente
        # mail_host = api.portal.get_tool(name='MailHost')
        # try:
        #     for user in annotations.keys():
        #         if annotations[user]['is_active']:
        #             mail_host.send(
        #                 body.getData(),
        #                 mto=annotations[user]['email'],
        #                 mfrom=sender,
        #                 subject=subject,
        #                 charset='utf-8',
        #                 msg_type='text/html'
        #             )
        # except SMTPRecipientsRefused:
        #     return UNHANDLED

        return OK
