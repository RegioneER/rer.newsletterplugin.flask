# -*- coding: utf-8 -*-
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from rer.newsletter.adapter.sender import IChannelSender
from rer.newsletter.utils import OK
from rer.newsletter.utils import SEND_UID_NOT_FOUND
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import logging

logger = logging.getLogger(__name__)


class SendCompletePost(Service):
    def reply(self):
        data = json_body(self.request)

        send_uid = data.get("send_uid", None)
        error = data.get("error", False)

        if not send_uid:
            self.request.response.setStatus(400)
            return dict(
                error=dict(type="BadRequest", message='Missing "send_uid" parameter')
            )
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        adapter = getMultiAdapter((self.context, self.request), IChannelSender)
        res = adapter.set_end_send_infos(send_uid=send_uid, completed=not error)
        if res != OK:
            if res == SEND_UID_NOT_FOUND:
                self.request.response.setStatus(500)
                return dict(
                    error=dict(
                        type="InternalServerError",
                        message='Send history "{uid}" not found in channel "{title}".'.format(  # noqa
                            uid=send_uid, title=self.context.title
                        ),
                    )
                )
            else:
                self.request.response.setStatus(500)
                return dict(
                    error=dict(
                        type="InternalServerError",
                        message="Unable to update end date. See application log for more details",  # noqa
                    )
                )
        self.request.response.setStatus(204)
        return
