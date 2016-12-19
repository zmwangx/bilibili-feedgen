#!/usr/bin/env python3

import os
import sys

import setuptools

if sys.version_info < (3, 6):
    sys.exit('Error: bilibili-feedgen requires Python 3.6 or later.')

here = os.path.dirname(os.path.realpath(__file__))
versionfile = os.path.join(here, 'bilibili_feedgen', 'version.py')

# Read version from version.py into __version__
with open(versionfile) as fp:
    exec(fp.read())

setuptools.setup(
    name='bilibili-feedgen',
    version=__version__,
    description='Bilibili user feed generator',
    url='https://github.com/zmwangx/bilibili-feedgen',
    author='Zhiming Wang',
    author_email='zmwangx@gmail.com',
    license='WTFPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Video',
    ],
    packages=['bilibili_feedgen'],
    install_requires=['arrow', 'feedgen', 'requests'],
    tests_require=['pytest'],
    entry_points={'console_scripts': [
        'bilibili-feedgen=bilibili_feedgen.generator:main',
    ]},
)
