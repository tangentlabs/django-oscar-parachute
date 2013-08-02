#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-oscar-parachute',
    version=":versiontools:parachute:",
    url='https://github.com/tangentlabs/django-oscar-parachute',
    author="Sebastian Vetter",
    author_email="sebastian.vetter@tangentsnowball.com.au",
    description="Importer for data from various other Ecommerce platforms",
    long_description=open('README.rst').read(),
    keywords="django, oscar, e-commerce, import, migration",
    license='BSD',
    platforms=['linux'],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=[
        'Django>=1.4.2',
        'dingus>=0.3.4',
        'django-oscar>=0.4',
    ],
    setup_requires=[
        'versiontools>=1.9.1',
    ],
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      #'License :: OSI Approved :: BSD License',
      'Operating System :: Unix',
      'Programming Language :: Python'
    ]
)
