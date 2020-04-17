# -*- coding: utf-8 -*-
from email.utils import formataddr
from plone.protect.authenticator import createToken
from rer.newsletter import logger
from rer.newsletter.adapter.base_adapter import BaseAdapter
from rer.newsletter.adapter.base_adapter import IChannelSender
from rer.newsletter.utility.channel import INVALID_CHANNEL
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
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

        nl = self._api(channel)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL

        flask_url = "http://127.0.0.1:5000/add-to-queue"

        # Costruzione del messaggio: body, subject, destinatari, ...
        body = self._getMessage(nl, message, unsubscribe_footer)

        nl_subject = ' - ' + nl.subject_email if nl.subject_email else u''
        subject = message.title + nl_subject

        response_email = nl.sender_email or "noreply@rer.it"
        sender = formataddr((nl.sender_name, response_email))
        token = createToken()

        # recipients = [annotations[user]['email'] for user in annotations.keys() if annotations[user]['is_active']]  # noqa
        recipients = []
        for user in annotations.keys():
            if annotations[user]['is_active']:
                recipients.append(annotations[user]['email'])

        # Preparazione della request con il vero payload e l'header
        headers = {"Content-Type": "application/json"}
        payload = {
                'channel_url': nl.absolute_url(),
                'subscribers': recipients,
                'subject': subject,
                'mfrom': sender,
                '_authenticator': token,
                'text': body.getData(),
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

        return OK
