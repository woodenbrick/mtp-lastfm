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
import gtk
import pygtk
pygtk.require("2.0")

import localisation
import lastfmtagger
_ = localisation.set_get_text()

class Songview(object):
    """An abstract class for creating windows showing song data in a textview"""
    def __init__(self, db, parent):
        self.parent = parent
        self.db = db
        self.path = os.path.join(self.parent.MAIN_PATH, "glade") + os.sep
        self.all_menu_items = {
            "love" : _("Love"), "ban" : _("Ban"),
            "dont-scrobble" : _("Don't Scrobble"),
            "tag" : _("Tag"), "ban-remove" : _("Remove Ban"),
            "love-remove" : _("Remove Love")}
        self.liststore = gtk.ListStore(int, str, str, str, gtk.gdk.Pixbuf, int)
        self.columns = ["Id", _("Artist"), _("Song"), _("Album"), _("Rating"), _("Playcount")]
        self.tree_view = self.create_window()
        self.tree_view.set_model(self.liststore)
        self.tree_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

    
    def create_window(self):
        self.window = gtk.Window()
        self.window.set_title(self.title)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_icon(gtk.gdk.pixbuf_new_from_file(self.path + self.icon))
        self.window.set_default_size(1000, 600)
        self.window.connect("destroy", self.on_window_destroy)
        scroller = gtk.ScrolledWindow()
        self.window.add(scroller)
        
        self.tree_view = gtk.TreeView()
        self.tree_view.set_name("treeview")
        self.tree_view.set_rubber_banding(True)
        self.tree_view.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_VERTICAL)
        #<property name="enable_tree_lines">True</property>
        self.tree_view.connect("button_press_event", self.on_tree_view_button_press_event)
        self.tree_view.show()
        scroller.show()
        scroller.add(self.tree_view)
        return self.tree_view
    
    def fill_liststore(self, data):
        """Loved/Banned lists: trackid, usecount, artist, song, album, rating
        Scrobble lists: trackid, scrobble_count, artist, song, album, rating"""
        for row in data:
            row5 = self.friendly_rating(row[5])
            self.liststore.append([row[0], row[2], row[3], row[4], row5, row[1]])
        
    def append_columns(self):
        i = 0
        for column in self.columns:
            col = gtk.TreeViewColumn(column)
            if i == 4 or i == 6:
                cell = gtk.CellRendererPixbuf()
            else:
                cell = gtk.CellRendererText()
            col.pack_start(cell, False)
            if i == 4 or i == 6:
                col.set_attributes(cell, pixbuf=i)
            else:
                col.set_attributes(cell, text=i)
            
            col.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            col.set_min_width(30)
            col.set_max_width(250)
            col.set_resizable(True)
            col.set_spacing(10)
            if i == 0:
                col.set_visible(False)
            self.tree_view.append_column(col)
            i +=1

    def create_right_click_menu(self, *args):
        """args are strings corresponding to keys in self.all_menu_items
        key: name, value: text, key + '.png': image"""
        menu = gtk.Menu()
        for key in args:
            image = gtk.Image()
            image.set_from_file(self.path + key + ".png")
            menu_item = gtk.ImageMenuItem(self.all_menu_items[key])
            menu_item.set_name(key)
            menu_item.set_image(image)
            if key == "tag":
                menu_item.connect("activate", self.on_tag_activated)
            else:
                menu_item.connect("activate", self.on_change_marking_activate)
            menu_item.show()
            menu.append(menu_item)    
        return menu
            
    def on_window_destroy(self, widget):
        self.parent.set_button_count()
    
    def friendly_rating(self, rating):
        """Parses the rating of an item and returns an image"""
        ratings = { "L" : "love.png", "B" : "ban.png",
                   "D" : "dont-scrobble.png"}
        try:
            image = self.path + ratings[rating]
        except KeyError:
            image = self.path + "ban-remove.png"
        return gtk.gdk.pixbuf_new_from_file(image)
    
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
                model.set_value(iter, 4, self.friendly_rating(marking))
            ids.append(model.get_value(iter, 0))
        return ids
    
    def on_change_marking_activate(self, widget):
        marking = self.get_marking(widget.name)
        id_list = self.get_selection(marking)
        self.db.change_markings(id_list, marking)
    
    def get_marking(self, widget_name):
        """Returns the appropriate marking to give to this item
        Possibilities are Loved, Banned, Don't Scrobble or Blank"""
        markings = {"love-remove" : "",
                    "ban-remove" : "",
                    "dont-scrobble" : "D",
                    "love" : "L",
                    "ban" : "B"}
        return markings[widget_name]
    
    def on_tag_activated(self, widget):
        """tagging is only applicable on a singular basis,
        so we only take the first row selected if we have multiples we disregard them"""
        model, rows = self.tree_view.get_selection().get_selected_rows()
        row = model[rows[0]]
        lastfmtagger.LastfmTagger(self.parent, row[1], row[2], row[3])


class CacheWindow(Songview):
    def __init__(self, db, parent):
        self.title = _("Cached Tracks")
        self.icon = "cache.png"
        Songview.__init__(self, db, parent)
        self.window.show()
        data = self.db.return_unique_scrobbles().fetchall()
        self.fill_liststore(data)
        self.append_columns()
        self.right_click_menu = self.create_right_click_menu("love", "ban",
                                                             "dont-scrobble", "tag")

    
class LovedWindow(Songview):
    def __init__(self, db, parent):
        self.title = _("Loved Tracks")
        self.icon = "love.png"
        Songview.__init__(self, db, parent)
        data = self.db.return_pending_love().fetchall()
        self.fill_liststore(data)
        self.right_click_menu = self.create_right_click_menu("love-remove", "tag")
        self.append_columns()
        self.window.show()

    def on_change_marking_activate(self, widget):
        #this is overridden so we can remove anything that was in the love_cache
        marking = self.get_marking(widget.name)
        id_list = self.get_selection(marking)
        self.db.change_markings(id_list, marking, was_love=True)

    def friendly_rating(self, rating):
        """Parses the rating of an item and returns a user friendly value
        in the future this will be an image"""
        if rating == "L":
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.path + "love.png")
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.path + "love-remove.png")
        return pixbuf


class BannedWindow(Songview):
    def __init__(self, db, parent):
        self.title = _("Banned Tracks")
        self.icon = "ban.png"
        Songview.__init__(self, db, parent)
        data = self.db.return_tracks("B").fetchall()
        self.fill_liststore(data)
        self.right_click_menu = self.create_right_click_menu("ban-remove", "tag")
        self.append_columns()
        self.window.show()
