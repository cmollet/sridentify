#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

NAME = 'sridentify'
DESCRIPTIOIN = 'Identify the EPSG code from a .prj file'
URL = 'https://github.com/cmollet/sridentify'
EMAIL = 'howtoreach@corymollet.com'
AUTHOR = 'Cory Mollet'
VERSION = '0.5.0'


with open('README.rst') as readme_file:
    readme = readme_file.read()


here = os.path.abspath(os.path.dirname(__file__))


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTIOIN,
    long_description=readme,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    package_data={'sridentify': ['epsg.db']},
    license="MIT",
    packages=["sridentify"],
    entry_points={
        'console_scripts': ['sridentify=sridentify.cli:main']
        },
    keywords='epsg, gis, shapefile, cli',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Utilities',
    ],
)
