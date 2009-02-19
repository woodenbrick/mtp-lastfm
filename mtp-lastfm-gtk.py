#!/usr/bin/env python
import sys
import gtk
import pygtk
import gtk.glade
pygtk.require("2.0")

import dbClass

def getPath():
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
            "on_options_clicked" : self.on_options_clicked,
        }
        self.tree.signal_autoconnect(event_handlers)
        
        #set window names
        self.main_window = self.tree.get_widget("main_window")
        self.options_window = self.tree.get_widget("options_window")
        self.login_window = self.tree.get_widget("login_window")
        #banned_window = self.tree.get_widget("banned_window")
        #cache_window = self.tree.get_widget("cache_window")
        
        #if a user was set to be logged in automatically, open the main window
        #otherwise show our login screen
        self.usersDB = dbClass.lastfmDb_Users()
        current_user = self.usersDB.get_users()
        if current_user is None:
            self.show_login_window()
        else:
            self.tree.get_widget("user").set_text(current_user[0])
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
        self.show_login_window()
        
    
    #menu options
    def on_options_clicked(self, widget):
        self.options_window.show()
    
    
    #This section deals with the LOGIN WINDOW
    def on_username_entry_focus_out_event(self, widget):
        print 'activation'
    
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
                self.usersDB.update_user(self.username, self.password)
            else:
                self.usersDB.remove_user(self.username)
 
    
    
if __name__ == "__main__":
    mtp = MTPLastfmGTK()
    gtk.main()


