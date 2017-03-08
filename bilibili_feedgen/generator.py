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

# requests session
import os
session = requests.Session()
session.headers.update({'Referer': 'https://space.bilibili.com/'})

def get_member_name(member_id: str) -> str:
    payload = {
        'mid': member_id,
    }
    api_url = 'https://space.bilibili.com/ajax/member/GetInfo'
    r = session.post(api_url, data=payload)
    assert r.status_code == 200
    data = r.json()['data']
    assert data['mid'] == member_id
    return data['name']

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
    api_url = ('https://space.bilibili.com/ajax/member/getSubmitVideos?%s' %
               urllib.parse.urlencode(query))
    r = session.get(api_url)
    assert r.status_code == 200
    try:
        return r.json()['data']['vlist']
    except (TypeError, KeyError):
        return []

def gen(feed_url: str, member_id: str, data: APIData, name : str = None,
        queries: List[Query] = None, output_file: str = None,
        only_write_on_change: bool = True) -> None:
    if not name:
        name = get_member_name(member_id)

    fg = feedgen.feed.FeedGenerator()
    fg.id(feed_url)
    fg.title(f"{name}'s Bilibili feed")
    fg.author({'name': name, 'uri': f'http://space.bilibili.com/{member_id}/'})
    fg.link(href=feed_url, rel='self', type='application/atom+xml')
    fg.link(href=f'http://space.bilibili.com/{member_id}', rel='alternate', type='text/html')

    created_last = arrow.get(-1).datetime
    for video in data:
        aid = video['aid']
        title = video['title']
        created = arrow.get(video['created']).datetime
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
        fe.published(created)
        fe.updated(created)
        fe.content(textwrap.dedent(f"""\
        <p><img src="{pic}"/></p>
        <p>Length: {length}</p>
        <p>{description}</p>"""), type='html')

        if created > created_last:
            created_last = created

    if created_last.timestamp() < 0:
        fg.updated(arrow.utcnow().datetime)
    else:
        fg.updated(created_last)

    atom = fg.atom_str(pretty=True).decode('utf-8')
    if output_file:
        if only_write_on_change:
            try:
                with open(output_file, 'r', encoding='utf-8') as fp:
                    old_atom = fp.read()
                    if old_atom == atom:
                        return
            except OSError:
                pass
        with open(output_file, 'w', encoding='utf-8') as fp:
            fp.write(atom)
    else:
        print(atom, end='')

# Returns True if successful, or False otherwise
def fetch_and_gen(options: argparse.Namespace, no_empty: bool = True) -> bool:
    member_id = options.member_id
    name = options.name
    count = options.count
    output_file = options.output_file
    force_write = options.force_write
    feed_url = options.feed_url
    queries = options.queries
    data = fetch(member_id, pagesize=count)
    if not data and no_empty:
        logger.error('API response does not contain data')
        return False
    gen(feed_url, member_id, data, name=name, queries=queries, output_file=output_file,
        only_write_on_change=not force_write)
    return True

def main():
    parser = getparser()
    options = parser.parse_args()
    options.queries = (None if not options.queries else
                       [filter_string.split() for filter_string in options.queries])
    sys.exit(0 if fetch_and_gen(options) else 1)
