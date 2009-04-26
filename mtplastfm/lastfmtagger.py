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

import gtk
import pygtk
import gobject

import webservices
import localisation

_ = localisation.set_get_text()

class LastfmTagger(object):
    
    def __init__(self, parent, artist, track, album):
        self.info = {"Track" : track,"Artist" : artist, "Album" : album }
        self.trans_info = { _("Track") : "Track", _("Artist") : "Artist",
                           _("Album") : "Album"}
        self.username = parent.username
        self.sk = parent.session_key
        self.wTree = gtk.glade.XML(parent.GLADE['tag'])
        self.fill_combo_box()
        self.prepare_treeview("popular_treeview")
        self.prepare_treeview("your_treeview")
        self.buffer = self.wTree.get_widget("tags").get_buffer()
        self.buffer.connect("changed", self.sanitise_tags)
        self.wTree.get_widget("window").show()
        self.set_tag_info(None)
        self.wTree.signal_autoconnect(self)
    
    
    def fill_combo_box(self):
        holder = self.wTree.get_widget("combobox_holder")
        self.combobox = gtk.combo_box_new_text()
        for key in self.trans_info.keys():
            self.combobox.append_text(key)
        self.combobox.show()
        holder.pack_start(self.combobox)
        self.combobox.set_active(0)
        self.combobox.connect("changed", self.set_tag_info)
        
    def set_tag_info(self, widget):
        cur_key = self.combobox.get_active_text()
        key = self.trans_info[cur_key]
        if key == "Artist":
            #.Translators:
            #sentence will be on the form of:
            #"Tagging Artist <name of artist>"
            self.wTree.get_widget("tag_info").set_text(_("Tagging %(type)s: %(name)s") %
                                                       {"type": cur_key,
                                                        "name" : self.info[key]}) 
        else:
            #.Translators:
            #This takes the form of either:
            #"Tagging Album <name of album> by Artist" or
            #"Tagging Track <name of track> by Artist"
            self.wTree.get_widget("tag_info").set_text(_("Tagging %(type)s: %(name)s by %(artist)s") %
                                                       {"type" : cur_key,
                                                        "name" : self.info[key],
                                                        "artist" : self.info['Artist']})
        while gtk.events_pending():
            gtk.main_iteration()
        #get popular tags and tags that the user has already used
        conn = webservices.LastfmWebService()
        #we will keep the user tags since they dont change
        try:
            self.user_tags
        except:
            self.user_tags = conn.get_user_top_tags(self.username)
            liststore = gtk.ListStore(str)
            for tag in self.user_tags:
                liststore.append([tag])
            self.wTree.get_widget("your_treeview").set_model(liststore)
            
        if cur_key == _("Album"):
            self.wTree.get_widget("popular_treeview").set_sensitive(False)
            return
        
        self.wTree.get_widget("popular_treeview").set_sensitive(True)
        popular_tags = conn.get_popular_tags(key.lower() + ".gettoptags", self.info)
        liststore = gtk.ListStore(str)
        for tag in popular_tags:
            liststore.append([tag])
        self.wTree.get_widget("popular_treeview").set_model(liststore)
        
        
        
    def prepare_treeview(self, treeview):
        if treeview == "popular_treeview":
            col_name = _("Popular tags")
        else:
            col_name = _("Your Tags")
        tree = self.wTree.get_widget(treeview)
        col = gtk.TreeViewColumn(col_name)
        cell = gtk.CellRendererText()
        col.pack_start(cell, False)
        col.set_attributes(cell, text=0)
        col.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        col.set_min_width(100)
        col.set_max_width(500)
        col.set_resizable(True)
        col.set_spacing(10)
        tree.append_column(col)
        
    def on_tag_row_activated(self, treeview, iter, col):
        """Adds the double clicked row to the list of tags to send"""
        model = treeview.get_model()
        tag = model[iter][0]
        tag.strip()
        start, end = self.buffer.get_bounds()
        if tag not in self.buffer.get_text(start, end):
            self.buffer.insert(end, tag + ",")
            self.sanitise_tags()

        
    def sanitise_tags(self, *args):
        """Removes whitespace and blank tags"""
        sanitised_tags = []        
        start, end = self.buffer.get_bounds()
        text = self.buffer.get_text(start, end)
        tags = text.split(",")    
        for tag in tags:
            clean = tag.strip()
            if clean in sanitised_tags:
                continue
            if clean != "":
                sanitised_tags.append(clean)
        
        if len(sanitised_tags) > 10 or len(sanitised_tags) == 0:
            self.wTree.get_widget("send_tags").set_sensitive(False)
        else:
            self.wTree.get_widget("send_tags").set_sensitive(True)
        return sanitised_tags
    
    
    def on_send_tags_clicked(self, widget):
        tags = self.sanitise_tags()    
        self.wTree.get_widget("tag_info").set_text(_("Sending tags"))
        cur_key = self.combobox.get_active_text()
        method = cur_key.lower() + ".addtags"
        conn = webservices.LastfmWebService()
        conn.send_tags(method, self.info, ",".join(tags), self.sk)
        self.wTree.get_widget("tag_info").set_text(_("Tags sent"))
        self.buffer.set_text("")
    
    def on_window_destroy(self, widget):
        self.wTree.get_widget("window").destroy()