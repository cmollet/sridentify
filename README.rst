sridentify
===========

Overview
--------

``sridentify`` is a command-line utility and Python API for quickly
identifying the `EPSG Registry Code <http://www.epsg-registry.org/>`__
from a ``.prj`` file typically associated with `ESRI
Shapefiles <https://en.wikipedia.org/wiki/Shapefile>`__. It ships with a
SQLite database containing mappings of `Well-known
Text <https://en.wikipedia.org/wiki/Well-known_text>`__ strings to EPSG
codes, the bulk of which was manually sourced and cleaned from `an ESRI
website <https://developers.arcgis.com/javascript/jshelp/pcs.html>`__.
It's not complete, however, and in the event you test it against a WKT
string not in the database it will search the
`prj2epsg.org <http://prj2epsg.org>`__ API. If the API returns an exact
match, that code is returned and saved to the SQLite database. Handling
several partial matches is currently planned, but not yet implemented.


Installation
------------

`pip install --user sridentify`

The `--user` is important, because the user running `sridentify` must have write
permissions on the SQLite database in the event that `sridentify` tries to save a new
result fetched from the `prj2epsg` API to the database.

TL;DR
-----

Command-Line usage
------------------

.. code:: bash

    $ sridentify seattle_land_use.prj
    2285

    # Example use in conjunction with the `shp2pgsql` command-line utility
    # that ships with PostGIS. Assuming you have a PostGIS-enabled database named `seattle`,
    # and you have a shapefile called `seattle_land_use` that you want to import into that database:

    $ shp2pgsql -s $(sridentify seattle_land_use.prj) -g the_geom -ID seattle_land_use.shp | psql -d seattle

Python API usage
-------------------

.. code:: python

    >>> from sridentify import sridentify

    >>> # Read .prj file from the filesystem
    >>> ident = sridentify()
    >>> ident.from_file('seattle_land_use.prj')
    >>> ident.get_epsg()
    2285

    >>> # Paste in Well-Known Text string directly
    >>> ident = sridentify(prj="""PROJCS["NAD_1983_StatePlane_Washington_North_FIPS_4601_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",1640416.666666667],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-120.8333333333333],PARAMETER["Standard_Parallel_1",47.5],PARAMETER["Standard_Parallel_2",48.73333333333333],PARAMETER["Latitude_Of_Origin",47.0],UNIT["Foot_US",0.3048006096012192]]""")
    >>> ident.get_epsg()
    2285


Background
----------

More and more governments and organizations are making their GIS data available to the public on
open data portals. Local governments typically store and use GIS data in the `map projection <https://en.wikipedia.org/wiki/Map_projection>`__ most appropriate for their location on planet Earth. For the United States, this is typically the `State Plane Coordinate System <https://en.wikipedia.org/wiki/State_Plane_Coordinate_System>`__. Other common systems are `Universal Transverse Mercator <https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system>`__, or a highly localized system that is accurate only within the geographic boundaries of the entity's jusrisdiction.

ESRI Shapefiles are a common format for publishing GIS data, although a "shapefile" with the ``.shp`` extension is really just data describing the geometry. Shapefiles are typically bundled with a ``dBase`` file ( ``.dbf`` extension ) which contains data attributes about the geometry and a small text file describing the spatial reference system of the geomtry in `Well-known text format <https://en.wikipedia.org/wiki/Well-known_text>`__.

Think of projections as character encoding for spatial data. Spatial
data lacking information about the coordinate system on which it has
been projected is all but useless, just as if you had text data in an
unknown encoding.

``sridentify`` is not meant to be a full-fledged client library to the actual
EPSG database, for that you're probably looking for something like `python-epsg <https://github.com/geo-data/python-epsg>`__

Rather, ``sridentify`` is for those looking to quickly identify the EPSG code
of a shapefile, especially when `importing into PostGIS <http://postgis.net/docs/manual-2.2/using_postgis_dbmanagement.html#shp2pgsql_usage>`__ . Of course, you could use `ogr2ogr <http://www.gdal.org/ogr2ogr.html>`__
to convert everything into a web-friendly projection, like:

.. code:: bash

    $ ogr2ogr -f PostgreSQL -t_srs EPSG:4326 PG:dbname=seattle seattle_land_use.shp

But transforming spatial data from one projection to another is a lossy operation
and can result in coordinate drift. Ideally, you would store the original data
in its original coordinate system and then transform copies as needed.

