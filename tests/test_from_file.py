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
        with self.assertRaises(UnicodeDecodeError):
            ident.from_file(
                os.path.join(
                    self.fixtures_dir,
                    'Central_Business_District.dbf'
                )
            )

    def test_non_text_file_does_not_raise_if_not_strict(self):

        ident = Sridentify(call_remote_api=False, strict=False)
        ident.from_file(
            os.path.join(
                self.fixtures_dir,
                'Central_Business_District.dbf'
            )
        )  # should not raise
        self.assertIsNone(ident.get_epsg())

    def test_from_file_on_large_file_does_not_load_entirety_into_memory(self):
        ident = Sridentify(call_remote_api=False, strict=False)
        ident.from_file(
            # on my system `du -b` reports this file to be 23004 bytes
            os.path.join(
                self.fixtures_dir,
                'Central_Business_District.shp'
            )
        )
        self.assertLess(
            sys.getsizeof(ident.prj),
            1200
            # from_file only requests the first 1024 bytes, but
            # there could be some GC overhead with sys.getsizeof,
            # so we mark it up a little bit here.
            # https://docs.python.org/3/library/sys.html#sys.getsizeof
        )
