# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from email.utils import formataddr
from persistent.dict import PersistentDict
from plone import api
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.adapter.base_adapter import BaseAdapter
from rer.newsletter.adapter.base_adapter import IChannelSender
from rer.newsletter.behaviors.ships import IShippable
from rer.newsletter.utility.channel import ALREADY_ACTIVE
from rer.newsletter.utility.channel import ALREADY_SUBSCRIBED
from rer.newsletter.utility.channel import INEXISTENT_EMAIL
from rer.newsletter.utility.channel import INVALID_CHANNEL
from rer.newsletter.utility.channel import INVALID_EMAIL
from rer.newsletter.utility.channel import INVALID_SECRET
from rer.newsletter.utility.channel import MAIL_NOT_PRESENT
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
from smtplib import SMTPRecipientsRefused
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.interface import Invalid


import json
import re
import uuid
import six

KEY = 'rer.newsletter.subscribers'


def mailValidation(mail):
    # valido la mail
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]' +
        '+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        raise Invalid(
            _(
                u'generic_problem_email_validation',
                default=u'Una o piu delle mail inserite non sono valide'
            )
        )
    return True


# da fixare la validazione
def uuidValidation(uuid_string):
    try:
        uuid.UUID(uuid_string, version=4)
    except ValueError:
        return False
    return True


def isCreationDateExpired(creation_date):
    # settare una data di scadenza di configurazione
    cd_datetime = datetime.strptime(creation_date, '%d/%m/%Y %H:%M:%S')
    t = datetime.today() - cd_datetime
    if t < timedelta(days=2):
        return True
    return False


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

        # costruisco il messaggio
        body = self._getMessage(nl, message, unsubscribe_footer)

        nl_subject = ' - ' + nl.subject_email if nl.subject_email else u''
        subject = message.title + nl_subject

        # costruisco l'indirizzo del mittente
        sender = formataddr((nl.sender_name, nl.sender_name))

        # invio la mail ad ogni utente
        mail_host = api.portal.get_tool(name='MailHost')
        try:
            for user in annotations.keys():
                if annotations[user]['is_active']:
                    mail_host.send(
                        body.getData(),
                        mto=annotations[user]['email'],
                        mfrom=sender,
                        subject=subject,
                        charset='utf-8',
                        msg_type='text/html'
                    )
        except SMTPRecipientsRefused:
            return UNHANDLED

        return OK
