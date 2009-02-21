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
#Foobar is distributed in the hope that it will be useful,
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

def get_path():
    """Finds the path that the script is running from"""
    path = os.path.dirname(os.path.realpath(__file__)) + '/'
    return path

class MTPLastfmGTK:
    def __init__(self):
        self.gladefile = "main_window.glade"
        self.tree = gtk.glade.XML(self.gladefile)
        event_handlers = {
            "on_main_window_destroy" : gtk.main_quit,
            "on_login_window_destroy" : gtk.main_quit,
            "on_login_clicked" : self.on_login_clicked,
            "on_logout_clicked" : self.on_logout_clicked,
            "on_username_entry_focus_out_event" : self.on_username_entry_focus_out_event,
            "on_check_device_clicked" : self.on_check_device_clicked,
            "on_options_clicked" : self.on_options_clicked,
            "on_apply_options_clicked" : self.on_apply_options_clicked,
            "on_cancel_options_clicked" : self.on_cancel_options_clicked,
            "on_about_clicked" : self.on_about_clicked,
            "on_about_closed" : self.on_about_closed
        }
        self.tree.signal_autoconnect(event_handlers)
        
        #set window names
        self.main_window = self.tree.get_widget("main_window")
        self.options_window = self.tree.get_widget("options_window")
        self.login_window = self.tree.get_widget("login_window")
        #banned_window = self.tree.get_widget("banned_window")
        #cache_window = self.tree.get_widget("cache_window")
        
        self.options_list = ("random", "alphabetical", "startup_check",
                        "auto_scrobble", "scrobble_time", "use_default_time")
        
        #if a user was set to be logged in automatically, open the main window
        #otherwise show our login screen
        self.usersDB = dbClass.lastfmDb_Users()
        current_user = self.usersDB.get_users()
        if current_user is None:
            self.show_login_window()
        else:
            self.tree.get_widget("user").set_text(current_user[0])
            self.username = current_user[0]
            self.show_main_window()
        
     
    
    def show_main_window(self):
        self.login_window.hide()
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
        path = get_path()
        self.write_info("Connecting to MTP device...")
        os.system("mtp-tracks > " + path + self.username + "tracklisting")
        f = file(path + self.username + "tracklisting", 'r').readlines()
        if len(f) < 3:
            self.write_info("MTP Device not found, please connect")
        else:
            self.write_info("Done. It is now safe to remove your MTP device")
            self.write_info("Cross checking song data with local database...")
            song_obj = songDataClass.songData()
            x = 1
            for line in f:
                song_obj.newData(line)
                if song_obj.readyForExport:
                    #add to db
                    song_obj.resetValues()
                    song_obj.newData(line)
                if x == 10:
                    break
                x += 1
            self.write_info("Done.", new_line=False)
        
    
    def write_info(self, new_info, new_line='\n', clear_buffer=False):
        """Writes data to the main window to let the user know what is going on"""
        buffer = self.tree.get_widget("info").get_buffer()
        if clear_buffer is True:
            buffer.set_text(new_info)
        else:
            start, end = buffer.get_bounds()
            info = buffer.get_text(start, end)
            if info is None:
                buffer.set_text(new_info)
            else:
                buffer.set_text(info + new_line + new_info)
    
    #menu options
    def on_options_clicked(self, widget):
        options = self.usersDB.retrieve_options(self.username)
        
        for i in range(0, len(self.options_list)):
            try:
                self.tree.get_widget(self.options_list[i]).set_active(options[i])
            except AttributeError:
                self.tree.get_widget(self.options_list[i]).set_value(options[i])
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
            self.show_main_window()
            self.tree.get_widget("user").set_text(self.username)
            if remember_password is True:
                #check if its already hashed
                if not re.findall(r"^([a-fA-F\d]{32})$", self.password):
                    self.password = md5.new(self.password).hexdigest()
                    
                self.usersDB.update_user(self.username, self.password)
            else:
                self.usersDB.remove_user(self.username)
                
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
        self.options_window.hide()
        
    
    #About Window
    def on_about_clicked(self, widget):
        self.tree.get_widget("about_dialog").show()
    
    def on_about_closed(self, widget):
        self.tree.get_widget("about_dialog").hide()
    
    
if __name__ == "__main__":
    mtp = MTPLastfmGTK()
    gtk.main()


