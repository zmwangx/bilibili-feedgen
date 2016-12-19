import argparse
import os
import tempfile
import xml.etree.ElementTree as ET

import requests

from bilibili_feedgen.generator import *

class TestGenerator:
    # Fetches data, generates a feed, then validate it with W3 Feed Validation
    # Service.
    def test_fetch_and_gen(self):
        try:
            fd, output_file = tempfile.mkstemp()
            os.close(fd)
            options = argparse.Namespace(
                member_id='1315101',
                count=5,
                output_file=output_file,
                feed_url='http://0.0.0.0:8000/atom.xml',
            )
            fetch_and_gen(options)

            with open(output_file) as fp:
                atom_str = fp.read()

            # Validate feed
            url = 'https://validator.w3.org/feed/check.cgi'
            payload = {
                'rawdata': atom_str,
                'output': 'soap12',
            }
            r = requests.post(url, data=payload)
            assert r.status_code == 200
            root = ET.fromstring(r.text)
            # Collect errors
            errors = [error for error in root.iter('error')]
            # Collect all warnings except SelfDoesntMatchLocation, which
            # is expected (we are checking rawdata rather than a url)
            warnings = [warning for warning in root.iter('warning')
                        if warning.find('type').text != 'SelfDoesntMatchLocation']
            # Collect all error and warning messages
            messages = [
                '%s:%s: %s' % (
                    t.find('line').text,
                    t.find('column').text,
                    t.find('text').text,
                ) for t in errors + warnings
            ]
            assert not errors and not warnings, '\n'.join(messages)
        finally:
            os.remove(output_file)
