# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PloneRestApiDXLayer
from plone.testing import z2

import rer.newsletterplugin.flask
import rer.newsletter
import plone.restapi


class RerNewsletterpluginFlaskLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rer.newsletter)
        self.loadZCML(package=rer.newsletterplugin.flask)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'rer.newsletter:default')
        applyProfile(portal, 'rer.newsletterplugin.flask:default')


RER_NEWSLETTERPLUGIN_FLASK_FIXTURE = RerNewsletterpluginFlaskLayer()


RER_NEWSLETTERPLUGIN_FLASK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_NEWSLETTERPLUGIN_FLASK_FIXTURE,),
    name='RerNewsletterpluginFlaskLayer:IntegrationTesting',
)


RER_NEWSLETTERPLUGIN_FLASK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_NEWSLETTERPLUGIN_FLASK_FIXTURE,),
    name='RerNewsletterpluginFlaskLayer:FunctionalTesting',
)


class RerNewsletterpluginFlaskAPILayer(PloneRestApiDXLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(RerNewsletterpluginFlaskAPILayer, self).setUpZope(
            app, configurationContext
        )

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rer.newsletter)
        self.loadZCML(package=rer.newsletterplugin.flask)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.restapi:default')
        applyProfile(portal, 'rer.newsletter:default')
        applyProfile(portal, 'rer.newsletterplugin.flask:default')


RER_NEWSLETTERPLUGIN_FLASK_API_FIXTURE = RerNewsletterpluginFlaskAPILayer()
RER_NEWSLETTERPLUGIN_FLASK_API_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_NEWSLETTERPLUGIN_FLASK_API_FIXTURE,),
    name="RerNewsletterpluginFlaskAPILayer:Integration",
)

RER_NEWSLETTERPLUGIN_FLASK_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_NEWSLETTERPLUGIN_FLASK_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="RerNewsletterpluginFlaskAPILayer:Functional",
)
