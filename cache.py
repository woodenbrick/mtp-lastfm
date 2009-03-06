#!/usr/bin/env python
import gtk
import pygtk
pygtk.require("2.0")
import gtk.glade

class CacheWindow:
    def __init__(self, glade_file, db, parent):
        
        self.parent = parent
        self.db = db
        self.wTree = gtk.glade.XML(glade_file)
        self.liststore = gtk.ListStore(int, str, str, str, str, int)
        self.cache_window = self.wTree.get_widget("cache_window")
        self.tree_view = self.wTree.get_widget("tree_view")
        self.tree_view.set_model(self.liststore)
        self.tree_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.right_click_menu = self.wTree.get_widget("right_click_menu")
        
        data = self.db.return_unique_scrobbles().fetchall()
        for row in data:
            if row[5] == "L":
                row5 = "Loved"
            else:
                row5 = ""
            self.liststore.append([row[0], row[2], row[3], row[4], row5, row[1]])
        
        columns = ["Id", "Artist", "Song", "Album", "Rating", "Count"]
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
            "on_cache_window_destroy" : self.on_cache_window_destroy,
            "on_tree_view_button_press_event" : self.on_tree_view_button_press_event,
            "on_change_marking_activate" : self.on_love_activate,
            "on_ban_activate" : self.on_ban_activate,
            "on_no_scrobble_activate" : self.on_no_scrobble_activate,
            }
        self.wTree.signal_autoconnect(handlers)
        
    def on_cache_window_destroy(self, widget):
        self.parent.set_cache_button()
    
    
    def on_tree_view_button_press_event(self, widget, event):
        """Show context menu on right click"""
        if event.button is 3:
            self.right_click_menu.popup(parent_menu_shell=None, parent_menu_item=None,
                                        func=None, button=event.button,
                                        activate_time=event.time)
            #returning True prevents the selection from being lost
            return True

    def on_love_activate(self, menuitem):
        current_selection = self.get_selection("Loved")
        self.db.change_markings(current_selection, "L")


    def on_ban_activate(self, menuitem):
        current_selection = self.get_selection("Banned")
        self.db.mark_songs_as_banned_or_no_scrobble(current_selection, "B")
    
    def on_no_scrobble_activate(self, menuitem):
        current_selection = self.get_selection("Don't Scrobble")
        self.db.mark_songs_as_banned_or_no_scrobble(current_selection)
        
    def get_selection(self, marking):
        """Looks at the treeview and returns the id numbers of the selected songs"""
        ids = []
        model, rows = self.tree_view.get_selection().get_selected_rows()
        for row in rows:
            iter = model.get_iter(row)
            model.set_value(iter, 4, marking)
            ids.append(model.get_value(iter, 0))
        return ids