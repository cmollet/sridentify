sridentify
===========

Overview
--------

``sridentify`` is a command-line utility and Python API for quickly
identifying the `EPSG Registry Code <http://www.epsg-registry.org/>`__
from a ``.prj`` file typically associated with `ESRI
Shapefiles <https://en.wikipedia.org/wiki/Shapefile>`__. It ships with an
SQLite database containing mappings of `Well-known
Text <https://en.wikipedia.org/wiki/Well-known_text_representation_of_coordinate_reference_systems>`__ strings to EPSG
codes, the bulk of which was manually sourced and cleaned from `an ESRI
website <https://developers.arcgis.com/javascript/jshelp/pcs.html>`__.
It's not complete, however, and in the event you test it against a WKT
string not in the database it can optionally search the
`prj2epsg.org <http://prj2epsg.org>`__ API. If the API returns an exact
match, that code is returned and saved to the SQLite database. Handling
several partial matches is currently planned, but not yet implemented. This feature can be disabled with the ``-n`` or ``--no-remote-api`` flags when running ``sridentify`` on the command line, or by instantiating with ``call_remote_api=False`` when using the Python API.

``sridentify`` is written in Python, 2- and 3-compatible, and has no external dependencies.


Installation
------------

``pip install --user sridentify``

The ``--user`` is important if installing system-wide (i.e., not in a virtualenv), because the
user running ``sridentify`` must have write permissions on the SQLite database in the event that
``sridentify`` tries to save a new result fetched from the ``prj2epsg`` API to the database.

On most Linux systems ``pip install --user`` will install to ``$HOME/.local`` and place the executable script
in ``$HOME/.local/bin``. You should add this to your ``$PATH`` if you want to run ``sridentify``
without having to specify the full location to the executable. On OS X and Windows ``pip install --user`` should install it to somewhere already in your ``$PATH``, but this may depend on how Python/pip was installed on those systems.

Quickstart
----------

Command-Line usage
------------------

::

    usage: sridentify [-h] [-n] prj

    Identify an EPSG code from a .prj file

    positional arguments:
      prj                  The .prj file

    optional arguments:
      -h, --help           show this help message and exit
      -n, --no-remote-api  Do not call the prj2epsg.org API if no match found in
                           the database

Cookbook
^^^^^^^^

Get the EPSG code from a ``.prj`` file

.. code:: bash

    $ sridentify seattle_land_use.prj
    2285

Example use in conjunction with the ``shp2pgsql`` command-line utility that ships with `PostGIS <http://postgis.net/>`__. Assuming you have a PostGIS-enabled database named ``seattle``, and you have a shapefile called ``seattle_land_use`` that you want to import into that database but you're not sure what spatial projection the shapefile uses::

    $ shp2pgsql -s $(sridentify seattle_land_use.prj) -g the_geom -ID seattle_land_use.shp | psql -d seattle

Do not call the prj2epsg.org API if no match found in the database (e.g., if running in a script or if the API is unresponsive)::

    $ sridentify --no-remote-api seattle_land_use.prj

Let's say you have a directory full of shapefiles of different projections that you want to bulk import into PostGIS. You could use ``sridentify -n`` in a script to skip calling the API for those that don't match anything in the database for speed's sake (and politeness of not hammering away at the free prj2epsg.org service!). For example:

.. code:: bash

    #!/usr/bin/env bash

    for p in $(find . -name "*.prj")
    do
        epsg="$(sridentify -n $p)"
        if [[ ! -z "$epsg" ]]
        then
            shp2pgsql -s $epsg -g the_geom -ID "${p/prj/shp}" | psql -d my_db_name
        else
            # log the unmatched prjs to a file
            echo "no EPSG code found for $p" >> bulk_import.log
        fi
    done

Python API usage
-------------------

.. code:: python

    >>> from sridentify import Sridentify

    >>> # Read .prj file from the filesystem
    >>> ident = Sridentify()
    >>> ident.from_file('/path/to/seattle_land_use.prj')
    >>> ident.get_epsg()
    2285

    >>> # Paste in Well-Known Text string directly
    >>> ident = Sridentify(prj="""PROJCS["NAD_1983_StatePlane_Washington_North_FIPS_4601_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",1640416.666666667],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-120.8333333333333],PARAMETER["Standard_Parallel_1",47.5],PARAMETER["Standard_Parallel_2",48.73333333333333],PARAMETER["Latitude_Of_Origin",47.0],UNIT["Foot_US",0.3048006096012192]]""")
    >>> ident.get_epsg()
    2285
    
    >>> # Do not call the prj2epsg.org API if no match found
    >>> ident = Sridentify(call_remote_api=False)
    >>> ident.from_file('foo.prj')
    >>> ident.get_epsg()  # would return None
    >>>

    >>> # Instantiate with strict=False to log errors and return None
    >>> # instead of raising Exceptions when trying to read in problematic files.
    >>> ident = Sridentify(strict=False)
    >>> # example: accidentally trying to read in a binary file
    >>> ident.from_file('seattle_land_use.shp') # this would log an error message
    >>> ident.get_epsg()  # would return None
    >>> ident = Sridentify(strict=True)  # the default
    >>> ident.from_file('seattle_land_use.shp')
    UnicodeDecodeError: 'utf-8' codec can't decode byte 0x88 in position 10: invalid start byte



Background
----------

More and more governments and organizations are making their GIS data available to the public on
open data portals. Local governments typically store and use GIS data in the `map projection <https://en.wikipedia.org/wiki/Map_projection>`__ most appropriate for their location on planet Earth. For the United States, this is typically the `State Plane Coordinate System <https://en.wikipedia.org/wiki/State_Plane_Coordinate_System>`__. Other common systems are `Universal Transverse Mercator <https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system>`__, or a highly localized system that is accurate only within the geographic boundaries of the entity's jusrisdiction.

ESRI Shapefiles are a common format for publishing GIS data, although a "shapefile" with the ``.shp`` extension is really just data describing the geometry. Shapefiles are typically bundled with a ``dBase`` file ( ``.dbf`` extension ) which contains data attributes about the geometry and a small text file describing the spatial reference system of the geomtry in WKT format.

``sridentify`` is not meant to be a full-fledged client library to the actual
EPSG database. If that's what you need, you're probably looking for something like `python-epsg <https://github.com/geo-data/python-epsg>`__.

Rather, ``sridentify`` is for those looking to quickly identify the EPSG code
of a shapefile, especially when `importing into PostGIS <http://postgis.net/docs/manual-2.2/using_postgis_dbmanagement.html#shp2pgsql_usage>`__. Of course, you could use `ogr2ogr <http://www.gdal.org/ogr2ogr.html>`__
to convert everything into a web-friendly projection, like:

.. code:: bash

    $ ogr2ogr -f PostgreSQL -t_srs EPSG:4326 PG:dbname=seattle seattle_land_use.shp

But transforming spatial data from one projection to another is a lossy operation
and can result in coordinate drift. Ideally, you would store the original data
in its original coordinate system and then transform copies as needed.

