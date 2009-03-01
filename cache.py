#!/usr/bin/env python
import gtk
import pygtk
pygtk.require("2.0")
import gtk.glade

class CacheWindow:
    def __init__(self, glade_file, cache_data):
        self.wTree = gtk.glade.XML(glade_file)
        self.liststore = gtk.ListStore(str, str, str, str, int)
        self.cache_window = self.wTree.get_widget("cache_window")
        self.tree_view = self.wTree.get_widget("treeview")
        self.tree_view.set_model(self.liststore)
        data = cache_data.fetchall()
        
        for row in data:
            self.liststore.append([row[2], row[3], row[4], row[5], row[1]])
        
        columns = ["Artist", "Song", "Album", "Rating", "Count"]
        i = 0
        total_width = 0
        for column in columns:
            cell = gtk.CellRendererText()
            col = gtk.TreeViewColumn(column)
            col.pack_start(cell, False)
            col.set_attributes(cell, text=i)
            col.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            col.set_min_width(30)
            col.set_max_width(300)
            col.set_resizable(True)
            col.set_spacing(10)
            self.tree_view.append_column(col)
            total_width = col.get_width()
            i+=1

        handlers = {}
        self.wTree.signal_autoconnect(handlers)
            
if __name__ == '__main__':
    tree = CacheWindow()
    gtk.main()