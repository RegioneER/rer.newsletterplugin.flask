# -*- coding: utf-8 -*-
"""Installer for the rer.newsletterplugin.flask package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join(
    [
        open('README.rst').read(),
        open('CONTRIBUTORS.rst').read(),
        open('CHANGES.rst').read(),
    ]
)


setup(
    name='rer.newsletterplugin.flask',
    version='1.0a1',
    description="Add-on per Plone collegato a rer.newsletter per inviare le mail usando un servizio Flask",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='RedTurtle',
    author_email='sviluppo@redturtle.it',
    url='https://github.com/collective/rer.newsletterplugin.flask',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/rer.newsletterplugin.flask',
        'Source': 'https://github.com/collective/rer.newsletterplugin.flask',
        'Tracker': 'https://github.com/collective/rer.newsletterplugin.flask/issues',
        # 'Documentation': 'https://rer.newsletterplugin.flask.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['rer', 'rer.newsletterplugin'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7, >=3.6",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'plone.api>=1.8.4',
        'plone.restapi',
        'plone.app.dexterity',
        'rer.newsletter',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
            'collective.MockMailHost',
            'requests-mock',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = rer.newsletterplugin.flask.locales.update:update_locale
    """,
)
