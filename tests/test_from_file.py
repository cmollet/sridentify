import unittest
import os
import sys

from sridentify import Sridentify



class FromFileTest(unittest.TestCase):

    def setUp(self):
        self.this_dir = os.path.abspath(os.path.dirname(__file__))
        self.fixtures_dir = os.path.join(self.this_dir, 'fixtures')
        self.prj_file = os.path.join(self.fixtures_dir, 'Central_Business_District.prj')
        self.fake_prj = os.path.join(self.fixtures_dir, 'not_a_real.prj')

    def test_non_text_file_raises_exception(self):
        ident = Sridentify(call_remote_api=False)
        ident.from_file(
            os.path.join(
                self.fixtures_dir,
                'Central_Business_District.dbf'
            )
        )
        with self.assertRaises(UnicodeDecodeError):
            ident.get_epsg()
