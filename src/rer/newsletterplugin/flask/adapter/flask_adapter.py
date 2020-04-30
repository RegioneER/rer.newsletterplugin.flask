# -*- coding: utf-8 -*-
from email.utils import formataddr
from rer.newsletter import logger
from rer.newsletter.adapter.sender import BaseAdapter
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.utils import NOK
from rer.newsletter.utils import OK
from rer.newsletter.utils import UNHANDLED
from zope.interface import implementer
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout

import json
import requests

SUBSCRIBERS_KEY = 'rer.newsletter.subscribers'
HISTORY_KEY = 'rer.newsletter.channel.history'
FLASK_URL = "http://127.0.0.1:5000/add-to-queue"


@implementer(IChannelSender)
class FlaskAdapter(BaseAdapter):
    """ Adapter per l'invio delle newsletter fuori da
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def sendMessage(self, message):
        logger.debug(
            'adapter: sendMessage %s %s', self.context.title, message.title
        )

        # Costruzione del messaggio: body, subject, destinatari, ...
        subscribers = self.get_annotations_for_channel(key=SUBSCRIBERS_KEY)
        recipients = []
        for user in subscribers.keys():
            if subscribers[user]['is_active']:
                recipients.append(subscribers[user]['email'])

        nl_subject = (
            ' - ' + self.context.subject_email
            if self.context.subject_email
            else u''
        )

        sender = (
            self.context.sender_name
            and formataddr(  # noqa
                (self.context.sender_name, self.context.sender_email)
            )
            or self.context.sender_email  # noqa
        )
        subject = message.title + nl_subject

        send_uid = self.set_start_send_infos(message=message)

        # Preparazione della request con il vero payload e l'header
        body = self.prepare_body(message=message)
        headers = {"Content-Type": "application/json"}
        payload = {
            'channel_url': self.context.absolute_url(),
            'subscribers': recipients,
            'subject': subject,
            'mfrom': sender,
            'text': body.getData(),
            'send_uid': send_uid,
        }
        try:
            response = requests.post(
                FLASK_URL, data=json.dumps(payload), headers=headers
            )
        except (ConnectionError, Timeout) as e:
            logger.exception(e)
            self.set_end_send_infos(send_uid=send_uid, completed=False)
            return NOK
        if response.status_code != 200:
            logger.error(
                "adapter: can't sendMessage %s %s",
                self.context.title,
                message.title,
            )
            return UNHANDLED

        return OK
