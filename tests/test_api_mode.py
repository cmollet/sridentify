import os
import unittest

from sridentify import Sridentify


# python2/3 compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class SridentifyAPIModeTest(unittest.TestCase):

    def setUp(self):
        self.this_dir = os.path.abspath(os.path.dirname(__file__))
        self.fixtures_dir = os.path.join(self.this_dir, 'fixtures')
        self.prj_file = os.path.join(self.fixtures_dir, 'street_center_lines.prj')
        self.ident = Sridentify()

    def test_from_file_raises_if_prj_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            self.ident.from_file('foo.prj')
            self.ident.from_file('')

    def test_get_epsg_from_file(self):
        self.ident.from_file(self.prj_file)
        self.assertEqual(self.ident.get_epsg(), 3435)

    def test_get_epsg_from_text_string(self):
        self.ident.prj = """PROJCS["NAD_1983_StatePlane_Illinois_East_FIPS_1201_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",984250.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-88.33333333333333],PARAMETER["Scale_Factor",0.999975],PARAMETER["Latitude_Of_Origin",36.66666666666666],UNIT["Foot_US",0.3048006096012192]]"""
        self.assertEqual(self.ident.get_epsg(), 3435)




if __name__ == '__main__':
    unittest.main()
