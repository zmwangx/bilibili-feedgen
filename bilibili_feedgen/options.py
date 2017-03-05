import argparse
import sys

from .version import __version__

class BetterArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print('error: %s\n' % message, file=sys.stderr)
        self.print_help()
        sys.exit(2)

def getparser() -> BetterArgumentParser:
    parser = BetterArgumentParser(description='Bilibili user feed generator.')
    add = parser.add_argument
    add('member_id',
        help='the id following space.bilibili.com/, e.g., 1315101')
    add('-c', '--count', default=30,
        help='number of latest videos to include (default is 30)')
    add('-f', '--filter', action='append', dest='queries', metavar='FILTER',
        help='''a filter is a space-delimited string containing one or
        more keywords, and an entry passes the filter only if it
        contains all the keywords (simple case-sensitive containment
        test); this option can be specified multiple times, and an entry
        only needs to pass one of the filters to appear; note that
        --count takes effect before filters are applied''')
    add('-o', '--output-file',
        help='write feed to file rather than print to stdout')
    add('--force-write', action='store_true',
        help='''force writing to output file; by default, if writing to
        file, do not actually overwrite it if feed content is
        unchanged''')
    add('-u', '--feed-url', default='http://0.0.0.0:8000/atom.xml',
        help='url where the feed will be served at')
    add('-V', '--version', action='version', version=__version__)
    return parser
