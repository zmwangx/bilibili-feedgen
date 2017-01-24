import argparse
import logging
import sys
import textwrap
import urllib.parse
from typing import Any, Dict, List

import arrow
import feedgen.feed
import requests

from .options import getparser

logging.basicConfig(
    format='[%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger('bilibili-feedgen')

# Types
APIData = List[Dict[str, Any]]
Query = List[str]

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
    try:
        return r.json()['data']['vlist']
    except (TypeError, KeyError):
        return []

def gen(feed_url: str, member_id: str, data: APIData,
        queries: List[Query] = None, output_file: str = None) -> None:
    if data:
        user = data[0]['author']
    else:
        user = f'User {member_id}'

    fg = feedgen.feed.FeedGenerator()
    fg.id(feed_url)
    fg.title(f"{user}'s Bilibili feed")
    fg.author({'name': user, 'uri': f'http://space.bilibili.com/{member_id}/'})
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

        if queries is not None:
            for query in queries:
                for keyword in query:
                    if keyword not in title and keyword not in description:
                        # Doesn't match this keyword, quit this query
                        break
                else:
                    # Matches all keywords in this query
                    break
            else:
                # Doesn't match any of the queries
                continue

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

# Returns True if successful, or False otherwise
def fetch_and_gen(options: argparse.Namespace, no_empty: bool = True) -> bool:
    member_id = options.member_id
    count = options.count
    output_file = options.output_file
    feed_url = options.feed_url
    queries = options.queries
    data = fetch(member_id, pagesize=count)
    if not data and no_empty:
        logger.error('API response does not contain data')
        return False
    gen(feed_url, member_id, data, queries=queries, output_file=output_file)
    return True

def main():
    parser = getparser()
    options = parser.parse_args()
    options.queries = (None if not options.queries else
                       [filter_string.split() for filter_string in options.queries])
    sys.exit(0 if fetch_and_gen(options) else 1)
