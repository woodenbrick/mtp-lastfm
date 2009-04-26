#!/usr/bin/python


from distutils.core import setup
import os
import glob 

PROGRAM_NAME = 'mtp-lastfm'
VERSION = '0.76'

glade_files = glob.glob(os.path.join("glade", "*.glade"))
print glade_files

desc = """Scrobble tracks from mtp device to last.fm"""

long_desc = """The purpose of this program is to scrobble tracks from mtp devices (such as the Creative Zen, or the Zune) to last.fm.  You can Love/Ban tracks before scrobbling, and also use the ratings on your device (5=Love, 1=Ban)."""
setup ( name = PROGRAM_NAME,
        version = VERSION,
        description = desc,
        long_description = long_desc,
        author = 'Daniel Woodhouse',
        author_email = 'wodemoneke@gmail.com',
	    license = 'GPLv3',
        platforms = ['Linux'],
        url = 'http://github.com/woodenbrick/mtp-lastfm/tree',
        packages = ['src'],
        data_files = [
            ('share/applications/', ['extras/mtp-lastfm.desktop']),
            ('share/mtp-lastfm/', ["glade", "l10n"]),
            ('bin/', ['bin/mtp-lastfm'])
        ])
