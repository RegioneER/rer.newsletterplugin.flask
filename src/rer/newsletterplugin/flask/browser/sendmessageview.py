# -*- coding: utf-8 -*-
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletterplugin.flask import _
from rer.newsletter.browser.message.sendmessageview import SendMessageView


class SendMessageViewCustom(SendMessageView):
    @property
    def success_message(self):
        return _(
            u'message_send',
            default=u'Message correctly enqueued to be sent to ${subscribers} '
            u'subscribers. Please check Channel history to know when '
            u'the task ends.',
            mapping=dict(subscribers=self.active_subscriptions),
        )


message_sending_view = wrap_form(
    SendMessageViewCustom,
    index=ViewPageTemplateFile('templates/sendmessageview.pt'),
)
