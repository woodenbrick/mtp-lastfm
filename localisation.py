# Copyright 2009 Daniel Woodhouse
#
#This file is part of mtp-lastfm.
#
#mtp-lastfm is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#mtp-lastfm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with mtp-lastfm.  If not, see http://www.gnu.org/licenses/
import os
import locale
import gettext
import gtk.glade

APP_NAME = "mtp-lastfm"
local_path = os.path.join(os.path.dirname(__file__), "l10n")
langs = []
lc, encoding = locale.getdefaultlocale()
if (lc):
    langs = [lc]
    language = os.environ.get('LANGUAGE', None)
    if (language):
        langs += language.split(":")
gettext.bindtextdomain(APP_NAME, local_path)
gettext.textdomain(APP_NAME)
gtk.glade.bindtextdomain(APP_NAME, local_path)
gtk.glade.textdomain(APP_NAME)

def set_get_text():
    lang = gettext.translation(APP_NAME, local_path,
                               languages=langs, fallback = True)
    return lang.gettext
