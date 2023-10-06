# Process a bunch of bible versions
#
#     Requires: 
#         List of version abrieviations
#     Optional :
#         delay override
#         isDebug override

from BibleVersionExtract import BibleVersionExtract

"""
Overrides are -<tag> followed by value:
-d <seconds> 
    set delay to that many seconds
-D <True | False>
    turn on (or off) debugging
"""

import argparse

parser = argparse.ArgumentParser(description='Parse and import bible versions if not up-to-date.',
                                 epilog="""
                                 For each version abbreviation attempt to import the full bible text, 
                                 skipping any chapters, books or versions 
                                 that have already been imported as the latest version.""")
parser.add_argument('versions', metavar='version', nargs='+',
                    help='an abbreiviation for a version of the bible')
parser.add_argument('--delay', dest='delay', action='store',
                    default=5, type=int,
                    help='seconds delay between web requests (default: 5)')
parser.add_argument('--verbose', dest='isDebug', action='store_const',
                    const=True, default=False, 
                    help='if to switch on debug')

args = parser.parse_args()

for version in args.versions:
    BibleVersionExtract(version, delay=args.delay, isDebug=args.isDebug)