#!/usr/bin/env python
import gtk
import pygtk
pygtk.require("2.0")
import gtk.glade

import songview.SongView

class LovedWindow(SongView):
    def __init__(self, glade_file, db, parent):
        Songview.__init__(self, glade_file, db, parent)
        data = self.db.return_tracks("L").fetchall()
        self.fill_liststore(data)
        columns = ["Id", "Artist", "Song", "Album", "Rating", "Plays"]
        self.append_columns(columns)
        new_handlers = {}
        self.handlers.update(new_handlers)
        self.wTree.signal_autoconnect(self.handlers)
