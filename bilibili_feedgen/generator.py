import argparse
import sys
import textwrap
import urllib.parse
from typing import Any, Dict, List

import arrow
import feedgen.feed
import requests

from .version import __version__

# Types
APIData = List[Dict[str, Any]]

class BetterArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print('error: %s\n' % message, file=sys.stderr)
        self.print_help()
        sys.exit(2)

# Returns a list of dicts with the following keys (and more):
# - aid (video url is http://www.bilibili.com/video/av{aid}/)
# - title
# - author
# - created (epoch time)
# - pic (url to the thumbnail)
# - description
# - length (MM:SS)
def fetch(member_id: str, pagesize: int = 30) -> APIData:
    query = {
        'mid': member_id,
        'pagesize': pagesize,
    }
    api_url = ('http://space.bilibili.com/ajax/member/getSubmitVideos?%s' %
               urllib.parse.urlencode(query))
    r = requests.get(api_url)
    assert r.status_code == 200
    return r.json()['data']['vlist']

def gen(feed_url: str, member_id: str, data: APIData, output_file: str = None) -> None:
    if data:
        user = data[0]['author']
    else:
        user = f'User {member_id}'

    fg = feedgen.feed.FeedGenerator()
    fg.id(feed_url)
    fg.title(f"{user}'s Bilibili feed")
    fg.link(href=feed_url, rel='self', type='application/atom+xml')
    fg.link(href=f'http://space.bilibili.com/{member_id}', rel='alternate', type='text/html')

    for video in data:
        aid = video['aid']
        title = video['title']
        created = video['created']
        pic = video['pic']
        description = video['description']
        length = video['length']
        url = f'http://www.bilibili.com/video/av{aid}/'

        fe = fg.add_entry()
        fe.id(url)
        fe.link(href=url, rel='alternate', type='text/html')
        fe.title(title)
        fe.published(arrow.get(created).datetime)
        fe.content(textwrap.dedent(f"""\
        <p><img src="{pic}"/></p>
        <p>Length: {length}</p>
        <p>{description}</p>"""), type='html')

    atom = fg.atom_str(pretty=True).decode('utf-8')
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as fp:
            fp.write(atom)
    else:
        print(atom, end='')

def main():
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
    args = parser.parse_args()
    member_id = args.member_id
    count = args.count
    output_file = args.output_file
    feed_url = args.feed_url

    gen(feed_url, member_id, fetch(member_id, pagesize=count), output_file=output_file)
