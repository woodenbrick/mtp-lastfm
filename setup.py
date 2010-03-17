#!/usr/bin/python

from DistUtilsExtra.command import *
from distutils.core import setup, Extension
import os
import glob 
import commands
PROGRAM_NAME = 'mtp-lastfm'
VERSION = '0.85'

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    return kw
#i would like to do the swig build here but cant figure out the correct
#way so we will just distribute the wrapper file
mtpconnect_module = Extension('mtplastfm/cmod/_mtpconnect', sources=[
    'mtplastfm/cmod/mtpconnect.c',
    'mtplastfm/cmod/mtpconnect_wrap.c'],
                           **pkgconfig("libmtp")
                           )
glade = glob.glob(os.path.join("glade", "*.glade"))
images = glob.glob(os.path.join("glade", "*.png"))
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
        packages = ['mtplastfm', 'mtplastfm.cmod'],
        ext_modules = [mtpconnect_module],
        data_files = [
            ('share/applications/', ['mtp-lastfm.desktop']),
            ('share/mtp-lastfm/', glade),
            ('share/mtp-lastfm/', images),
            ('bin/', ['mtp-lastfm'])],
       cmdclass = {"build" :  build_extra.build_extra,
                   "build_i18n" :  build_i18n.build_i18n,
                 }
)
