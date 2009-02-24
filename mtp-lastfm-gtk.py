#!/usr/bin/env python

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
import sys
import re
import md5
import gtk
import pygtk
import gtk.glade
pygtk.require("2.0")

import dbClass
import songDataClass
import scrobbler

__author__ = "Daniel Woodhouse"
__version__ = "0.1-dev"

def get_path():
    if "dev" in __version__:
        print 'Development version'
        return os.path.dirname(__file__)
    else:
        return "/usr/local/applications/mtp-lastfm/"

class MTPLastfmGTK:
    def __init__(self):
        
        self.HOME_DIR = os.path.join(os.environ['HOME'], ".mtp-lastfm") + os.sep
        self.MAIN_PATH = get_path()
        try:
            os.mkdir(self.HOME_DIR)
        except OSError:
            pass
        
        self.gladefile = os.path.join(self.MAIN_PATH, "glade", "gui.glade")
        self.tree = gtk.glade.XML(self.gladefile)
        event_handlers = {
            "on_main_window_destroy" : gtk.main_quit,
            "on_login_window_destroy" : gtk.main_quit,
            "on_login_clicked" : self.on_login_clicked,
            "on_logout_clicked" : self.on_logout_clicked,
            "on_username_entry_focus_out_event" : self.on_username_entry_focus_out_event,
            "on_check_device_clicked" : self.on_check_device_clicked,
            "on_scrobble_clicked" : self.on_scrobble_clicked,
            "on_scrobble_time_entered_clicked" : self.on_scrobble_time_entered_clicked,
            "on_options_clicked" : self.on_options_clicked,
            "on_apply_options_clicked" : self.on_apply_options_clicked,
            "on_cancel_options_clicked" : self.on_cancel_options_clicked,
            "on_cache_clicked" : self.on_cache_clicked,
            "on_about_clicked" : self.on_about_clicked,
        }
        self.tree.signal_autoconnect(event_handlers)
        
        self.main_window = self.tree.get_widget("main_window")
        self.options_window = self.tree.get_widget("options_window")
        self.login_window = self.tree.get_widget("login_window")
        #banned_window = self.tree.get_widget("banned_window")
        #cache_window = self.tree.get_widget("cache_window")
        
        #if a user was set to be logged in automatically, open the main window
        #otherwise show our login screen
        self.usersDB = dbClass.lastfmDb_Users(self.HOME_DIR)
        current_user = self.usersDB.get_users()
        if current_user is None:
            self.show_login_window()
        else:
            self.tree.get_widget("user").set_text(current_user[0])
            self.username = current_user[0]
            self.password = current_user[1]
            #authenticate user with lastfm
            if self.authenticate_user():
                self.options = Options(self.username, self.usersDB)
                if not os.path.exists(self.HOME_DIR + self.username + 'DB'):
                    self.write_info("User db doesn't exist, creating.")
                    create_new = True
                else:
                    create_new = False
                self.song_db = dbClass.lastfmDb(self.HOME_DIR + self.username + "DB", create_new)
                self.show_main_window()
            else:
                self.tree.get_widget("login_error").set_text(self.authentication_error)
                self.show_login_window()
            
    def show_main_window(self):
        self.login_window.hide()
        self.write_info("User authenticated.")
        self.main_window.show()
        
    def show_options_window(self):
        self.options_window.show()
        
    def show_login_window(self):
        self.main_window.hide()
        self.login_window.show()
        
    
    # This section deals with the MAIN WINDOW
        
    def on_logout_clicked(self, widget):
        self.tree.get_widget("username_entry").set_text("")
        self.tree.get_widget("password_entry").set_text("")
        self.tree.get_widget("login_error").set_text("")
        self.show_login_window()
    
    def on_check_device_clicked(self, widget):
        self.write_info("Connecting to MTP device...")
        os.system("mtp-tracks > " + self.HOME_DIR + self.username + "tracklisting")
        f = file(self.HOME_DIR + self.username + "tracklisting", 'r').readlines()
        if len(f) < 3:
            self.write_info("MTP Device not found, please connect")
        else:
            self.write_info("Done. It is now safe to remove your MTP device\n\
                            Cross checking song data with local database...")
            song_obj = songDataClass.songData()
            for line in f:
                song_obj.newData(line)
                if song_obj.readyForExport:
                    self.song_db.addNewData(song_obj)
                    song_obj.resetValues()
                    song_obj.newData(line)
            self.write_info("Done.", new_line='')
    
    def authenticate_user(self):
        """This authenticates the user with last.fm ie. The Handshake"""
        self.tree.get_widget("login_error").set_text("Authenticating...")
        while gtk.events_pending():
            gtk.main_iteration(False)
        self.scrobbler = scrobbler.Scrobbler(self.username, self.password)
        server_response, msg = self.scrobbler.handshake()
        if server_response == "OK":
            return True
        else:
            self.authentication_error = msg
            return False
            
    
    def on_scrobble_clicked(self, widget):
        """Scrobbles tracks to last.fm"""
        #show scrobble dialog, if user has indicated in preferences
        if self.options.return_option("use_default_time") is True:
            scr_time = self.options.return_option("scrobble_time")
        else:
            self.show_scrobble_dialog()
            scr_time = self.tree.get_widget("scrobble_time_manual").get_value()
        self.scrobbler.setScrobbleTime(scr_time)
        scrobble_list = self.song_db.returnScrobbleList()
        if self.scrobbler.submitTracks(scrobble_list):
                self.song_db.deleteScrobbles('all')
        else:
            self.song_db.deleteScrobbles(scrobble.deletionIds)                
        self.write_info(msg)
    
    def show_scrobble_dialog(self):
        self.tree.get_widget("scrobble_time_manual").set_value(self.options.return_option("scrobble_time"))
        (self.options.return_option("scrobble_time"))
        self.tree.get_widget("scrobble_dialog").run()
        
    def on_scrobble_time_entered_clicked(self, widget):
        self.tree.get_widget("scrobble_dialog").hide()
        
    def on_cache_clicked(self, widget):
        data_set = self.song_db.returnScrobbleList()
        listing = []
        for row in data_set:
            listing.append( row[2]+ " " + row[3] + " " + str(row[1]))
        listing = "\n".join(listing)
        self.write_info(listing, buffer_name="cache_buffer", clear_buffer=True)
        self.tree.get_widget("cache_window").show()
    
    def write_info(self, new_info, buffer_name="info", new_line='\n', clear_buffer=False):
        """Writes data to the main window to let the user know what is going on"""
        buffer = self.tree.get_widget(buffer_name).get_buffer()
        if clear_buffer is True:
            buffer.set_text(new_info)
        else:
            start, end = buffer.get_bounds()
            info = buffer.get_text(start, end)
            if info is None:
                buffer.set_text(new_info)
            else:
                buffer.set_text(info + new_line + new_info)
        while gtk.events_pending():
            gtk.main_iteration(False)




    #menu options
    def on_options_clicked(self, widget):
        for o in self.options.options_list:
            try:
                self.tree.get_widget(o).set_active(self.options.return_option(o))
            except AttributeError:
                self.tree.get_widget(o).set_value(self.options.return_option(o))
        self.options_window.show()
    
    
    #This section deals with the LOGIN WINDOW
    def on_username_entry_focus_out_event(self, widget, key):
        entry = self.tree.get_widget("username_entry").get_text()
        user = self.usersDB.user_exists(entry)
        if user is not False:
            self.tree.get_widget("password_entry").set_text(user[1])
        
    def on_login_clicked(self, widget):
        self.username = self.tree.get_widget("username_entry").get_text()
        self.password = self.tree.get_widget("password_entry").get_text()
        remember_password = self.tree.get_widget("remember_password").get_active()
        
        if self.username == '' or self.password == '':
            login_error = self.tree.get_widget("login_error")
            login_error.set_text("Error: Please enter a username and password")
        else:
            if not re.findall(r"^([a-fA-F\d]{32})$", self.password):
                self.password = md5.new(self.password).hexdigest()
            if self.authenticate_user():
                self.show_main_window()
                self.tree.get_widget("user").set_text(self.username)
                if remember_password is True:
                    self.usersDB.update_user(self.username, self.password)
                else:
                    self.usersDB.remove_user(self.username)
            else:
                self.show_login_window()
                self.tree.get_widget("login_error").set_text(self.authentication_error)
                
    #this section deals with the OPTIONS WINDOW
    def on_cancel_options_clicked(self, widget):
        self.options_window.hide()
        
    
    def on_apply_options_clicked(self, widget):
        random = self.tree.get_widget("random").get_active()
        alpha = self.tree.get_widget("alphabetical").get_active()
        startup_check = self.tree.get_widget("startup_check").get_active()
        auto_scrobble = self.tree.get_widget("auto_scrobble").get_active()
        scrobble_time = self.tree.get_widget("scrobble_time").get_value()
        use_default_time = self.tree.get_widget("use_default_time").get_active()
        self.usersDB.update_options(self.username, random, alpha,
                                    startup_check, auto_scrobble,
                                    scrobble_time, use_default_time)
        self.options = self.options.reset_options(self.username, self.usersDB)
        self.options_window.hide()
        
    
    #About Window
    def on_about_clicked(self, widget):
        self.tree.get_widget("about_dialog").set_website("http://www.google.com")
        response = self.tree.get_widget("about_dialog").run()
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            self.tree.get_widget("about_dialog").hide()
        
class Options:
    def __init__(self, username, db):
        self.options_list = ("random", "alphabetical", "startup_check",
                        "auto_scrobble", "scrobble_time", "use_default_time")
        self.reset_options(username, db)
        
    def reset_options(self, username, db):
        options = db.retrieve_options(username)
        self.dic_options = self.create_option_dic(options)
        
    def create_option_dic(self, options):
        dic = {}
        for o in range(0, len(self.options_list)):
            dic[self.options_list[o]] = options[o]
        return dic
    
    def return_option(self, option_name):
        return self.dic_options[option_name]
        
        
if __name__ == "__main__":
    mtp = MTPLastfmGTK()
    gtk.main()


