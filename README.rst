.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==========================
rer.newsletterplugin.flask
==========================

Questo prodotto serve per "spostare" l'invio delle newsletter del prodotto
``rer.newsletter`` al di fuori di Plone. L'obiettivo è rendere il tutto più
flessibile e fluido appoggiandosi ad un'app Flask che penserà a gestire
l'intero job di invio e comunicare a Plone l'esito dell'operazione.

Vedi: ``rer.newsletterdispatcher.flask``.


Features
--------

- Can be bullet points


Translations
------------

This product has been translated into

- Italiano


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
