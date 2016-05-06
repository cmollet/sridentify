epsg\_ident
===========

Overview
--------

``epsg_ident`` is a command-line utility and Python module for quickly
identifying the `EPSG Registry Code <http://www.epsg-registry.org/>`__
from a ``.prj`` file typically associated with `ESRI
Shapefiles <https://en.wikipedia.org/wiki/Shapefile>`__. It ships with a
SQlite3 database containing mappings of `Well-known
Text <https://en.wikipedia.org/wiki/Well-known_text>`__ strings to EPSG
codes, the bulk of which was manually sourced and cleaned from `an ESRI
website <https://developers.arcgis.com/javascript/jshelp/pcs.html>`__.
It's not complete, however, and in the event you test it against a WKT
string not in the database it will search the
`prj2epsg.org <http://prj2epsg.org>`__ API. If the API returns an exact
match, that code is returned and saved to the SQLite database. Handling
several partial matches is currently planned, but not yet implemented.

TL;DR
-----

Command-Line usage
------------------

.. code:: bash

    $ epsg_ident seattle_land_use.prj
    2285

Python module usage
-------------------

.. code:: python

    >>> from epsg_ident import EpsgIdent

    >>> # Read .prj file from the filesystem
    >>> ident = EpsgIdent()
    >>> ident.read_prj_from_file('seattle_land_use.prj')
    >>> ident.get_epsg()
    2285

    >>> # Paste in Well-Known Text string directly
    >>> ident = EpsgIdent(prj="""PROJCS["NAD_1983_StatePlane_Washington_North_FIPS_4601_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",1640416.666666667],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-120.8333333333333],PARAMETER["Standard_Parallel_1",47.5],PARAMETER["Standard_Parallel_2",48.73333333333333],PARAMETER["Latitude_Of_Origin",47.0],UNIT["Foot_US",0.3048006096012192]]""")
    >>> ident.get_epsg()
    2285


Background
----------

Think of projections as character encoding for spatial data. Spatial
data lacking information about the coordinate system on which it has
been projected is all but useless, just as if you had text data in an
unknown encoding.

``epsg_ident`` is not meant to be a full-fledged client library to the actual
EPSG database, for that you're probably looking for something like `python-epsg <https://github.com/geo-data/python-epsg>`__

Rather, ``epsg_ident`` is for those looking to quickly identify the EPSG code
of a shapefile, especially when `importing into PostGIS <http://postgis.net/docs/manual-2.2/using_postgis_dbmanagement.html#shp2pgsql_usage>`__ . Of course, you could use `ogr2ogr <http://www.gdal.org/ogr2ogr.html>`__ 
to convert everything into a web-friendly projection, like:

.. code:: bash

    $ ogr2ogr -f PostgreSQL -t_srs EPSG:4326 PG:dbname=seattle seattle_land_use.shp

But transforming spatial data from one projection to another is a lossy operation
and can result in coordinate drift. Ideally, you would store the original data
in its original coordinate system and then transform copies as needed.

