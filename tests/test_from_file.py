import os
import unittest

from sridentify import Sridentify


class SridentifyTest(unittest.TestCase):

    def setUp(self):
        self.this_dir = os.path.abspath(os.path.dirname(__file__))
        self.fixtures_dir = os.path.join(self.this_dir, 'fixtures')
        self.prj_file = os.path.join(self.fixtures_dir, 'street_center_lines.prj')

    def test_get_epsg_from_file(self):
        ident = Sridentify()
        ident.from_file(self.prj_file)
        self.assertEqual(ident.get_epsg(), 3435)


if __name__ == '__main__':
    unittest.main()
