#!/usr/bin/env python
import sys
import gtk
import pygtk
import gtk.glade
pygtk.require("2.0")

class MTPLastfmGTK:
    def __init__(self):
        self.gladefile = "main_window.glade"
        self.tree = gtk.glade.XML(self.gladefile)
        event_handlers = {
            "on_main_window_destroy" : gtk.main_quit,
            "on_options_clicked" : self.on_options_clicked,
        }
        self.tree.signal_autoconnect(event_handlers)
        
    def on_options_clicked(self, widget):
        print 'Options'
        option_window = self.tree.get_widget("options_window")
        option_window.show()    
    
if __name__ == "__main__":
    mtp = MTPLastfmGTK()
    gtk.main()


