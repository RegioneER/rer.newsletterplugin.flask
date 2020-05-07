# -*- coding: utf-8 -*-
from email.utils import formataddr
from plone import api
from rer.newsletter import logger
from rer.newsletter.adapter.sender import BaseAdapter
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.browser.settings import ISettingsSchema
from rer.newsletter.utils import NOK
from rer.newsletter.utils import OK
from rer.newsletter.utils import UNHANDLED
from rer.newsletterplugin.flask import _
from rer.newsletterplugin.flask.interfaces import (
    INewsletterPluginFlaskSettings,
)
from zope.interface import implementer
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout

import json
import re
import requests

SUBSCRIBERS_KEY = 'rer.newsletter.subscribers'
HISTORY_KEY = 'rer.newsletter.channel.history'


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
        queue_endpoint = api.portal.get_registry_record(
            'queue_endpoint',
            interface=INewsletterPluginFlaskSettings,
            default=u'',
        )
        if not queue_endpoint:
            api.portal.show_message(
                message=_(
                    u'endpoint_not_set',
                    default=u'Queue endpoint not set. Please set it in site controlpanel.',  # noqa
                ),
                request=self.context.REQUEST,
                type='error',
            )
            return NOK
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
            'channel_url': self.convert_url(self.context.absolute_url()),
            'subscribers': recipients,
            'subject': subject,
            'mfrom': sender,
            'text': body.getData(),
            'send_uid': send_uid,
        }
        try:
            response = requests.post(
                queue_endpoint, data=json.dumps(payload), headers=headers
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

    def convert_url(self, url):
        source_link = api.portal.get_registry_record(
            'source_link', ISettingsSchema
        )
        if not source_link:
            source_link = api.portal.get().absolute_url()

        destination_link = api.portal.get_registry_record(
            'destination_link', ISettingsSchema
        )

        # non è questo il modo migliore per fare il replace...
        # 1. non serve usare re.sub ma basta il replace di string
        # 2. forse sarebbe più corretto usare un metodo di lxml
        if source_link and destination_link:
            return re.sub(source_link, destination_link, url)
        return url
