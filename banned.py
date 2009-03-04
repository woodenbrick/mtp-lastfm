#!/usr/bin/env python
import gtk
import pygtk
pygtk.require("2.0")
import gtk.glade

class BannedWindow:
    def __init__(self, glade_file, db, parent):
        
        self.parent = parent
        self.db = db
        self.wTree = gtk.glade.XML(glade_file)
        self.liststore = gtk.ListStore(int, str, str, str)
        self.cache_window = self.wTree.get_widget("banned_window")
        self.tree_view = self.wTree.get_widget("tree_view")
        self.tree_view.set_model(self.liststore)
        self.tree_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        data = self.db.return_banned_tracks().fetchall()
        for row in data:
            self.liststore.append([row[0], row[1], row[2], row[3]])
        
        columns = ["Id", "Artist", "Song", "Album"]
        i = 0
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
            i +=1
            
        handlers = {
            "on_banned_window_destroy" : self.on_banned_window_destroy,
            "on_close_ban_clicked" : self.on_close_ban_clicked,
            "on_tree_view_button_press_event" : self.on_tree_view_button_press_event,
            "on_remove_ban_clicked" : self.on_remove_ban_clicked
            }
        self.wTree.signal_autoconnect(handlers)
        
    def on_banned_window_destroy(self, widget):
        self.parent.set_cache_button()
    
    
    def on_tree_view_button_press_event(self, widget, event):
        if event.button is 3:
            #returning True prevents the selection from being lost
            return True

    def on_close_ban_clicked(self, widget):
        self.wTree.get_widget("ban_window").destroy()
        self.parent.set_cache_button()
    
    def on_remove_ban_clicked(self, widget):
        selected = self.get_selection()
        self.db.remove_ban(selected)

    def get_selection(self):
        """Looks at the treeview and returns the id numbers of the selected songs"""
        ids = []
        model, rows = self.tree_view.get_selection().get_selected_rows()
        for row in rows:
            iter = model.get_iter(row)
            model.set_value(iter, 1, "Unbanned")
            ids.append(model.get_value(iter, 0))
        return ids