#!/usr/bin/env python
import gtk
import pygtk
pygtk.require("2.0")
import gtk.glade

class SongView(object):
    """An abstract class for creating windows showing song data in a textview"""
    def __init__(self, glade_file, db, parent):
        
        self.parent = parent
        self.db = db
        self.wTree = gtk.glade.XML(glade_file)
        self.liststore = gtk.ListStore(int, str, str, str, str, int)
        self.cache_window = self.wTree.get_widget("window")
        self.tree_view = self.wTree.get_widget("tree_view")
        self.tree_view.set_model(self.liststore)
        self.tree_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.right_click_menu = self.wTree.get_widget("right_click_menu")
        self.handlers = {
            "on_window_destroy" : self.on_cache_window_destroy,
            "on_tree_view_button_press_event" : self.on_tree_view_button_press_event,
            }
    
    def fill_liststore(self, data):
        """
        Loved/Banned lists look like this:
        trackid, usecount, artist, song, album, rating
        Scrobble lists look like this:
        trackid, scrobble_count, artist, song, album, rating"""
        for row in data:
            row5 = self.friendly_rating(row[5])
            self.liststore.append([row[0], row[2], row[3], row[4], row5, row[1]])
        
    def append_columns(self, column_headers):
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

        
    def on_window_destroy(self, widget):
        self.parent.set_cache_button()
    
    def friendly_rating(self, rating):
        """Parses the rating of an item and returns a user friendly value
        in the future this will be an image"""
        if rating == "L":
            return "Loved"
        if rating == "B":
            return "Banned"
        return ""
    
    def on_tree_view_button_press_event(self, widget, event):
        """Show context menu on right click"""
        if event.button is 3:
            self.right_click_menu.popup(parent_menu_shell=None, parent_menu_item=None,
                                        func=None, button=event.button,
                                        activate_time=event.time)
            #returning True prevents the selection from being lost
            return True
   
    def get_selection(self, marking):
        """Looks at the treeview and returns the id numbers of the selected songs"""
        ids = []
        model, rows = self.tree_view.get_selection().get_selected_rows()
        for row in rows:
            iter = model.get_iter(row)
            model.set_value(iter, 4, marking)
            ids.append(model.get_value(iter, 0))
        return ids