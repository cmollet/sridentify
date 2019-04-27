# -*- coding: utf-8 -*-
import json
import logging
import os
import sqlite3
import sys

try:
    # python 3.x
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode
except ImportError:
    # falls back to python2.x
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

logger = logging.getLogger(__name__)
log_fmt = '%(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)


class Sridentify(object):

    def __init__(
        self,
        dbpath=None,
        prj=None,
        epsg_code=None,
        mode='api',
        call_remote_api=True,
        strict=True
    ):
        self.dbpath = dbpath
        self.prj = prj
        self.epsg_code = epsg_code
        self.mode = mode
        self.call_remote_api = call_remote_api
        self.strict = strict

        if self.dbpath is None:
            self.dbpath = os.path.abspath(os.path.join(
                os.path.dirname(__file__), 'epsg.db'
            ))
        elif not os.path.exists(self.dbpath):
            raise FileNotFoundError("%s not found" % self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)

    def handle_error(self, exc, msg):
        """
        Determine how to handle an error and what message to
        display to the user.
        :param exc: Exception
        :param msg: str, the message to display to the user
        :return: None
        """
        if self.mode == "api":
            logger.error(msg)
            if self.strict:
                raise exc
        elif self.mode == "cli":
            sys.stderr.write(msg)
            sys.exit(1)

    def from_file(self, path):
        if not os.path.exists(path):
            self.handle_error(
                FileNotFoundError,
                "ERROR - No such file: '{}'".format(path)
            )
        with open(path, "rb") as fp:
            try:
                self.prj = fp.read(1024)
            except IOError as exc:
                self.handle_error(
                    exc,
                    """ERROR - Unable to read\n{}\nfrom the filesystem.
                Does it exist and do you have the necessary permissions?\n""".format(path)
            )
        try:
            self.prj = self.prj.decode('utf-8')
        except UnicodeDecodeError as exc:
            self.handle_error(
                exc,
                "ERROR: {} does not appear to be a .prj file or is in an unknown character encoding".format(path)
            )

    def get_epsg(self):
        """
        Attempts to determine the EPSG code for a given PRJ file or other
        similar text-based spatial reference file.

        First, it looks up the PRJ text in the included epsg.db SQLite
        database, which was manually sourced and cleaned from an ESRI website,
        https://developers.arcgis.com/javascript/jshelp/pcs.html

        If it cannot be found there, it next tries the prj2epsg.org API.
        If an exact match is found, that EPSG code is returned and saved to
        the database to avoid future external API calls.

        TODO:
        If that API cannot find an exact match but several partial matches,
        those partials will be displayed to the user with the option to select one to save to the
        database.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT epsg_code FROM prj_epsg WHERE prjtext = ?", (self.prj,))
        # prjtext has a unique constraint on it, we should only ever fetchone()
        result = cur.fetchone()
        if not result and self.call_remote_api:
            return self.call_api()
        elif result is not None:
            self.epsg_code = result[0]
            return self.epsg_code

    def call_api(self):
        url = 'http://prj2epsg.org/search.json?'
        params = {
            'mode': 'wkt',
            'terms': self.prj
        }
        try:
            req = urlopen(url + urlencode(params))
        except HTTPError as http_exc:
            logger.warning("""Failed to retrieve data from prj2epsg.org API:\n
                            Status: %s \n
                            Message: %s""" % (http_exc.code, http_exc.msg))
        else:
            raw_resp = req.read()
            try:
                resp = json.loads(raw_resp.decode('utf-8'))
            except json.JSONDecodeError:
                logger.warning(
                    'API call succeeded but response is not JSON '
                    'and was not saved to the database. '
                    'Actual response was: \n%s' % raw_resp
                )
                return
            return self.process_api_result(resp)

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
            cur = self.conn.cursor()
            cur.execute(
                """INSERT INTO prj_epsg (prjtext, epsg_code) VALUES(?, ?)""",
                (self.prj, self.epsg_code)
            )
        except self.conn.IntegrityError:
            # This shouldn't ever happen unless the user tries to manually
            # enter a prjtext that already exists
            self.conn.rollback()
            logger.warning("%s is already in the database" % self.prj)
        self.conn.commit()

    def from_epsg(self, epsg_code):
        """
        Loads self.prj by epsg_code.
        If prjtext not found returns False.
        """
        self.epsg_code = epsg_code
        assert isinstance(self.epsg_code, int)
        cur = self.conn.cursor()
        cur.execute("SELECT prjtext FROM prj_epsg WHERE epsg_code = ?", (self.epsg_code,))
        result = cur.fetchone()
        if result is not None:
            self.prj = result[0]
            return True

        return False


    def to_prj(self, filename):
        """
        Saves prj WKT to given file.
        """
        with open(filename, "w") as fp:
            fp.write(self.prj)