# -*- coding: utf-8 -*-
import json
import logging
import os
import sqlite3
from urllib import request
from urllib.parse import urlencode
import click

logger = logging.getLogger(__name__)
log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)


class EpsgIdent:

    def __init__(self, dirname=os.path.dirname(os.path.abspath(__file__)),
                 dbname='esri_epsg.db', dbpath=None, prj=None, conn=None,
                 cur=None, epsg_code=None):
        self.dirname = dirname
        self.dbname = dbname
        self.dbpath = dbpath
        self.prj = prj
        self.conn = conn
        self.cur = cur
        self.epsg_code = epsg_code

        if self.dbpath is None:
            self.dbpath = os.path.join(self.dirname, self.dbname)
        elif not os.path.exists(self.dbpath):
            logger.error("%s does not seem to exist" % self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)
        self.cur = self.conn.cursor()

    def read_prj_from_file(self, path):
        if not os.path.exists(path):
            logger.error("%s does not appear to be a valid path,\
                         try using the absolute path" % path)
        try:
            fp = open(path)
            self.prj = fp.read()
        except IOError:
            logger.warn("Unable to read %s from the filesystem" % path)

    def get_epsg(self):
        """
        Attempts to determine the EPSG code for a given PRJ file or other
        similar text-based spatial reference file.

        First, it looks up the PRJ text in the included esri_epsg.db SQLite
        database, which was manually sourced and cleaned from an ESRI website,
        https://developers.arcgis.com/javascript/jshelp/pcs.html

        If it cannot be found there, it next tries the prj2epsg.org API.
        If an exact match is found, that EPSG code is returned and saved to
        the database to avoid future external API calls. If that API cannot
        find an exact match but several partial matches, those partials will be
        displayed to the user with the option to select one to save to the
        database.

        TODO:
        Pretty-print the PRJ with hints for each entry.
        """
        self.cur.execute("SELECT epsg_code FROM prj_epsg WHERE prjtext = ?",
                         (self.prj,))
        # prjtext has a unique constraint on it, we should only ever fetchone()
        result = self.cur.fetchone()
        if not result:
            self.call_api()
        else:
            self.epsg_code = result[0]
            return self.epsg_code

    def call_api(self):
        url = 'http://prj2epsg.org/search.json?'
        params = {
                'mode': 'wkt',
                'terms': self.prj
                }
        try:
            req = request.urlopen(url+urlencode(params))
        except request.HTTPError as http_exc:
            logger.warning("""Failed to retrieve data from prj2epsg.org API:\n
                            Status: %s \n
                            Message: %s""" % (http_exc.code, http_exc.msg))
        else:
            raw_resp = req.read()
            try:
                resp = json.loads(raw_resp.decode('utf-8'))
            except json.JSONDecodeError:
                logger.warning('API call succeeded but response\
                        is not JSON: %s' % raw_resp)
            self.process_api_result(resp)

    def process_api_result(self, api_resp):
        if api_resp.get('exact'):
            self.epsg_code = int(api_resp['codes'][0]['code'])
            self.save_to_db()
            return self.epsg_code
        elif api_resp.get('codes'):
            # TODO: prompt user to pick one
            pass

    def save_to_db(self):
        # SQLite lets you declare column data types but doesn't actually
        # enforce them:
        # https://www.sqlite.org/datatype3.html
        assert isinstance(self.epsg_code, int)
        try:
            self.cur.execute("""INSERT INTO prj_epsg (prjtext, epsg_code) VALUES
                    (?, ?)""", (self.prj, self.epsg_code))
        except self.conn.IntegrityError:
            # XXX: This shouldn't ever happen unless the user tries to manually
            # enter a prjtext that already exists
            self.conn.rollback()
            logger.warn("%s is already in the database" % self.prj)
        self.conn.commit()


@click.command()
@click.argument('prjfile', type=click.File())
def cli(prjfile):
    prjtext = prjfile.read()
    ident = EpsgIdent(prj=prjtext)
    click.echo(ident.get_epsg())
