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


class SendCompletePost(Service):
    def reply(self):
        data = json_body(self.request)

        send_uid = data.get("send_uid", None)

        if not send_uid:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest", message='Missing "send_uid" parameter'
                )
            )

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        adapter = getMultiAdapter((self.context, self.request), IChannelSender)
        try:
            res = adapter.set_end_send_infos(send_uid=send_uid)
        except Exception:
            plone_utils = api.content.get_view(
                name="plone_utils", context=self.context, request=self.request
            )
            exception = plone_utils.exceptionString()
            self.request.response.setStatus(500)
            return dict(
                error=dict(type="InternalServerError", message=exception)
            )
        if res != OK:
            if res == SEND_UID_NOT_FOUND:
                self.request.response.setStatus(404)
                return dict(
                    error=dict(
                        type="NotFound",
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
                        message='Unable to update end date. See application log for more details',  # noqa
                    )
                )
        return self.reply_no_content()
