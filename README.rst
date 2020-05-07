===========================
RER Newsletter plugin Flask
===========================

This is a plugin for `rer.newsletter <https://github.com/RegioneER/rer.newsletter>`_ that moves outside from Plone the task for sending emails.

It is made to work with `rer.newsletterdispatcher.flask <https://github.com/RegioneER/rer.newsletterdispatch.flask>`_ natively, but can work
with every endpoint that exposes the same route and replies in the same way.

The main problem having mail dispatcher into Plone, is that this task can take a lot of time (we have some cases with 70000 subscriptions)
and block the instance for a large amount of time slowing down the site and cause also some conflict errors.


Features
--------

This product register a new adapter for IChannelSender that overrides some basic rer.newsletter methods and send to an external
endpoint all informations to send the newsletter.

This process is asyncronous, so the channel history will be updated only when the endpoint calls the site with the status of the task.


External endpoint address
-------------------------

You can set the endpoint address into Plone's registry searching for "flask" entry or going directly here:
``http://your_plone_site/portal_registry/edit/rer.newsletterplugin.flask.interfaces.INewsletterPluginFlaskSettings.queue_endpoint``

If the addesss is not set, the newsletter will not be send.

Completed task notification
---------------------------

When the external process finish its job (succesfully or with an error), calls a plone.restapi endpoint ('@send-done') registered
for newsletter Channels to update the channel about the status of that job.

Translations
------------

This product has been translated into

- Italian


Installation
------------

Install rer.newsletterplugin.flask by adding it to your buildout::

    [buildout]

    ...

    eggs =
        rer.newsletterplugin.flask


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/RegioneER/rer.newsletterdispatcher.flask/issues
- Source Code: https://github.com/RegioneER/rer.newsletterdispatcher.flask


License
-------

The project is licensed under the GPLv2.

Credits
-------

Developed with the support of `Regione Emilia Romagna <http://www.regione.emilia-romagna.it/>`_;

Regione Emilia Romagna supports the `PloneGov initiative <http://www.plonegov.it/>`_.

Authors
-------

This product was developed by **RedTurtle Technology** team.

.. image:: https://avatars1.githubusercontent.com/u/1087171?s=100&v=4
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
