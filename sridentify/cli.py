import argparse
import sys
from sridentify import Sridentify


parser = argparse.ArgumentParser(
        description="Identify an EPSG code from a .prj file",
        )

parser.add_argument('prj', help="The .prj file")


def main():
    args = parser.parse_args()
    sridentifier = Sridentify(mode='cli')
    sridentifier.from_file(args.prj)
    srid = sridentifier.get_epsg()
    if srid is not None:
        sys.stdout.write(str(srid) + '\n')
