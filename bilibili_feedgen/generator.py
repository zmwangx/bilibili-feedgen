import argparse
import textwrap
import urllib.parse
from typing import Any, Dict, List

import arrow
import feedgen.feed
import requests

from .options import getparser

# Types
APIData = List[Dict[str, Any]]

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

def fetch_and_gen(options: argparse.Namespace) -> None:
    member_id = options.member_id
    count = options.count
    output_file = options.output_file
    feed_url = options.feed_url
    gen(feed_url, member_id, fetch(member_id, pagesize=count), output_file=output_file)

def main():
    parser = getparser()
    options = parser.parse_args()
    fetch_and_gen(options)
