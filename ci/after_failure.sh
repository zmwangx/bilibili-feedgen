#!/usr/bin/env bash
set -x
./setup.py install
bilibili-feedgen -c 5 1315101 | tee invalid-feed.atom
curl -sS -X POST --data-urlencode "rawdata=$(<invalid-feed.atom)" --data-urlencode 'output=soap12' \
     https://validator.w3.org/feed/check.cgi | xmllint --format -
curl -F "file=@invalid-feed.atom" https://file.io
