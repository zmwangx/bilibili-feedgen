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
    parser.add_argument('member_id',
                        help='the id following space.bilibili.com/, e.g., 1315101')
    parser.add_argument('-c', '--count', default=30,
                        help='number of latest videos to include (default is 30)')
    parser.add_argument('-o', '--output-file',
                        help='write feed to file rather than print to stdout')
    parser.add_argument('-u', '--feed-url', default='http://0.0.0.0:8000/atom.xml',
                        help='url where the feed will be served at')
    parser.add_argument('-V', '--version', action='version', version=__version__)
    return parser
