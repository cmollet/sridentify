#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'Click',
    'flake8',
    'tox',
    'twine'
]


setup(
    name='epsg_ident',
    version='0.1.1',
    description="Quickly get the EPSG code from a .prj file or WKT",
    long_description=readme,
    author="Cory Mollet",
    author_email='cory@corymollet.com',
    url='https://github.com/cmollet/epsg_ident',
    package_data={'epsg_ident': ['esri_epsg.db']},
    install_requires=requirements,
    license="ISCL",
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        epsg_ident=epsg_ident:cli
        ''',
    keywords='epsg, gis, shapefile',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Utilities',
    ],
)
