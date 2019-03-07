import argparse
import sys
from sridentify import Sridentify


parser = argparse.ArgumentParser(
    description="Identify an EPSG code from a .prj file",
)
parser.add_argument(
    'prj',
    help="The .prj file"
)
parser.add_argument(
    '-n',
    '--no-remote-api',
    action='store_false',
    dest='call_remote_api',
    help='Do not call the prj2epsg.org API if no match found in the database'
)


def main():
    args = parser.parse_args()
    sridentifier = Sridentify(mode='cli', call_remote_api=args.call_remote_api)
    sridentifier.from_file(args.prj)
    srid = sridentifier.get_epsg()
    if srid is not None:
        sys.stdout.write(str(srid) + '\n')
