#!/usr/bin/env python
import gtk
import pygtk
pygtk.require("2.0")
import gtk.glade
import time
import webservices
import gobject

class Songview(object):
    """An abstract class for creating windows showing song data in a textview"""
    def __init__(self, glade_file, db, parent):
        
        self.parent = parent
        self.db = db
        self.wTree = gtk.glade.XML(glade_file)
        self.liststore = gtk.ListStore(int, str, str, str, str, int) #gtk.gdk.Pixbuf, int)
        self.columns = ["Id", "Artist", "Song", "Album", "Rating", "Plays"]
        self.tree_view = self.wTree.get_widget("tree_view")
        self.tree_view.set_model(self.liststore)
        self.tree_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.right_click_menu = self.wTree.get_widget("right_click_menu")
        self.handlers = {
            "on_window_destroy" : self.on_window_destroy,
            "on_tree_view_button_press_event" : self.on_tree_view_button_press_event,
            "on_change_marking_activate" : self.on_change_marking_activate
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
        
    def append_columns(self):
        i = 0
        for column in self.columns:
            col = gtk.TreeViewColumn(column)
            cell = gtk.CellRendererText()
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
            pixbuf = gtk.gdk.pixbuf_new_from_file("glade/heart.png")
        elif rating == "B":
            pixbuf = gtk.gdk.pixbuf_new_from_file("glade/banned.png")
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file("glade/ban-remove.png")
        return rating
    
    def on_tree_view_button_press_event(self, widget, event):
        """Show context menu on right click"""
        if event.button is 3:
            self.right_click_menu.popup(parent_menu_shell=None, parent_menu_item=None,
                                        func=None, button=event.button,
                                        activate_time=event.time)
            #returning True prevents the selection from being lost
            return True
   
    def get_selection(self, marking=None):
        """Looks at the treeview and returns the id numbers of the selected songs
        marking is the optional value you want to set the affected rows to"""
        ids = []
        model, rows = self.tree_view.get_selection().get_selected_rows()
        for row in rows:
            iter = model.get_iter(row)
            if marking is not None:
                model.set_value(iter, 4, marking)
            ids.append(model.get_value(iter, 0))
        return ids
    
    def on_change_marking_activate(self, widget):
        marking = self.get_marking(widget.name)
        id_list = self.get_selection(marking)
        self.db.change_markings(id_list, marking)
    
    def get_marking(self, widget_name):
        """Returns the appropriate marking to give to this item
        Possibilities are Loved, Banned, Don't Scrobble or Blank"""
        markings = {"remove_love" : "",
                    "remove_ban" : "",
                    "no_scrobble" : "D",
                    "love" : "L",
                    "ban" : "B"}
        return markings[widget_name]
    


class CacheWindow(Songview):
    def __init__(self, glade_file, db, parent):
        Songview.__init__(self, glade_file, db, parent)
        self.set_love_auth_state()
        data = self.db.return_unique_scrobbles().fetchall()
        self.fill_liststore(data)
        self.columns = ["Id", "Artist", "Song", "Album", "Rating", "Count"]
        self.append_columns()
        self.wTree.get_widget("window").show()
        new_handlers = {
            
            }
        self.handlers.update(new_handlers)
        self.wTree.signal_autoconnect(self.handlers)
    
    def set_love_auth_state(self):
        if self.parent.session_key:
            self.wTree.get_widget("main_container").remove(self.wTree.get_widget("auth_area"))
        else:
            new_handlers = {
                "on_love_auth_button_clicked" : self.on_love_auth_button_clicked
            }
            self.handlers.update(new_handlers)
            
            
    
    def on_love_auth_button_clicked(self, widget):
        auth_dialog = self.wTree.get_widget("auth_dialog")
        #self.wTree.get_widget("auth_ok").set_sensitive(False)
        webservice = webservices.LastfmWebService()
        token = webservice.request_session_token()
        webservice.request_authorisation(token)
        response = auth_dialog.run()
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            auth_dialog.hide()
        else:
            valid, session_key = webservice.create_web_service_session(token)
            if valid is True:
                self.parent.usersDB.add_key(self.parent.username, session_key)
                self.wTree.get_widget("love_auth_state").set_text("Authentication complete")
                self.wTree.get_widget("love_auth_button").hide()
                self.parent.session_key = session_key
            else:
                self.wTree.get_widget("love_auth_state").set_text(session_key)
            auth_dialog.hide()
    
    
    
class LovedWindow(Songview):
    def __init__(self, glade_file, db, parent):
        Songview.__init__(self, glade_file, db, parent)
        data = self.db.return_tracks("L").fetchall()
        self.fill_liststore(data)
        self.append_columns()
        new_handlers = {
            
            }
        self.handlers.update(new_handlers)
        self.wTree.signal_autoconnect(self.handlers)
        
    def on_change_marking_activate(self, widget):
        #this is overridden so we can remove anything that was in the love_cache
        marking = self.get_marking(widget.name)
        id_list = self.get_selection(marking)
        self.db.change_markings(id_list, marking, was_love=True)


class BannedWindow(Songview):
    def __init__(self, glade_file, db, parent):
        Songview.__init__(self, glade_file, db, parent)
        data = self.db.return_tracks("B").fetchall()
        self.fill_liststore(data)
        self.append_columns()
        
        new_handlers = {
            }
        self.handlers.update(new_handlers)
        self.wTree.signal_autoconnect(self.handlers)
        


  