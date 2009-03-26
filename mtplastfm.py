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
import gobject
import threading
gtk.gdk.threads_init()
import time
pygtk.require("2.0")

import dbClass
from songdata import SongData
import scrobbler
import songview
import webservices
from progressbar import ProgressBar
from options import Options


def get_path():
    return os.path.dirname(__file__)

        
def connect_to_mtp_device(filename):
    """Run in a seperate thread"""
    os.system("mtp-tracks > " + filename)



class MTPLastfmGTK:
    def __init__(self, author, version, error_log=False, test_mode=False):
        self.test_mode = test_mode
        self.error_log = error_log
        self.author = author
        self.version = version
        self.HOME_DIR = os.path.join(os.environ['HOME'], ".mtp-lastfm") + os.sep
        self.MAIN_PATH = get_path()

        self.GLADE = {}
        for file in "gui cache ban love log".split(" "):
            self.GLADE[file] = os.path.join(self.MAIN_PATH, "glade", file + ".glade")
            
        try:
            os.mkdir(self.HOME_DIR)
        except OSError:
            pass
        
        if self.error_log:
            log_file = self.HOME_DIR + "errors.log"
            sys.stderr = open(log_file, 'a')
            print 'Error messages will be logged in %s' % log_file 
        self.tree = gtk.glade.XML(self.GLADE['gui'])
        self.tree.signal_autoconnect(self)
        
        self.main_window = self.tree.get_widget("main_window")
        self.options_window = self.tree.get_widget("options_window")
        self.login_window = self.tree.get_widget("login_window")
        self.tree.get_widget("info").get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(
            gtk.gdk.Cursor(gtk.gdk.ARROW))
        
        about_dialog = self.tree.get_widget("about_dialog")
        about_dialog.set_version(self.version)
        about_dialog.set_authors(self.author)

        self.usersDB = dbClass.lastfmDb_Users(self.HOME_DIR)
        current_user = self.usersDB.get_users()
        self.show_login_window()
        if current_user is not None:
            self.username = current_user[0]
            self.password = current_user[1]
            if self.authenticate_user():
                self.setup_user_session()
            else:
                self.tree.get_widget("login_error").set_text(self.authentication_error)
    
  
    def show_main_window(self):
        self.login_window.hide()
        self.write_info("User authenticated.", clear_buffer=True)
        self.main_window.show()
        while gtk.events_pending():
            gtk.main_iteration(False)

        
    def show_login_window(self):
        self.main_window.hide()
        self.login_auto_completer()
        self.login_window.show()
        
    def on_main_window_destroy(self, widget):
        gtk.main_quit()

 
    def on_logout_clicked(self, widget):
        self.tree.get_widget("username_entry").set_text("")
        self.tree.get_widget("password_entry").set_text("")
        self.tree.get_widget("login_error").set_text("")
        self.show_login_window()
        
  
    def on_check_device_clicked(self, widget):
        self.write_info("Connecting to MTP device")
        dump_file = self.HOME_DIR + "mtp-dump_" + self.username
        progress_bar = ProgressBar(self.tree.get_widget("progressbar"),
                                       update_speed=100, pulse_mode=True)
        if not self.test_mode:
            #threaded in case libmtp stops responding
            conn = threading.Thread(target=connect_to_mtp_device, args=([dump_file]))
            start_time = time.time()
            conn.daemon = True
            conn.start()
            while conn.isAlive():
                if time.time() - start_time > 15:
                    self.write_info("libmtp seems to be having trouble closing the session with your device.")
                    break
        progress_bar.run_timer(finished=True)
        f = file(dump_file, 'r').readlines()
        if len(f) < 3:
            self.write_info("Device not found, no tracklisting to check.")
        else:
            self.write_info("Done.", new_line=" ")
            self.write_info("It is now safe to remove your device")
            if self.first_run:
                self.write_info("Populating database for first time (may take a while)")
            else:
                self.write_info("Cross checking song data with local database...")
            self.song_db.pending_scrobble_list = None
            song_obj = SongData(self.song_db, self.HOME_DIR, self)
    
            progress_bar = ProgressBar(self.tree.get_widget("progressbar"), len(f), 0)
            for line in f:
                while gtk.events_pending():
                    gtk.main_iteration()
                song_obj.check_new_data(line)
                progress_bar.current_progress += 1
            progress_bar.run_timer(finished=True)

            self.song_db.pending_scrobble_list = None
            if song_obj.song_count % 100 != 0:
                self.write_info("%d tracks checked" % song_obj.song_count)
            self.write_info("Complete.")
            if song_obj.error_count > 0:
                self.write_info("%d items were not added to your song database." % song_obj.error_count + "\n")
                
                buffer = self.tree.get_widget("info").get_buffer()
                iter = buffer.get_end_iter()
                anchor = buffer.create_child_anchor(iter)
                button = gtk.Button(label=None, stock="gtk-info")
                button.show()
                self.tree.get_widget("info").add_child_at_anchor(button, anchor)
                button.connect("clicked", self.show_error_details, "songdata")
            self.song_db.update_scrobble_count()
            self.set_button_count()
            
            if self.options.return_option("auto_scrobble") == True:
                self.on_scrobble_clicked(None)
                
    
    def show_error_details(self, widget, data):
        if data is "songdata":
            tree = gtk.glade.XML(self.GLADE['log'])
            f = open(self.HOME_DIR + "db.log", "r").read()
            self.write_info(new_info=f, text_widget=tree.get_widget("text_view"),
                            clear_buffer=True)
            tree.get_widget("window").show()
    
    def set_button_count(self):
        """Checks if we should set a value for a button or disable it"""
        buttons = {
            "love" :
                [len(self.song_db.return_pending_love().fetchall()),
                "loved_label"],
            
            "ban" :
                [len(self.song_db.return_tracks("B").fetchall()),
                "banned_label"],
                
            "cache" :
                [self.song_db.scrobble_counter,
                "cache_label"]}
        
        for key, value in buttons.items():
            if value[0] is 0:
                sensitivity = False
                text = ""
            else:
                sensitivity = True
                text = "(" + str(value[0]) + ")"
            
            self.tree.get_widget(value[1]).set_text(text)
            self.tree.get_widget(key).set_sensitive(sensitivity)
   
    def authenticate_user(self):
        """This authenticates the user with last.fm ie. The Handshake"""
        #disable all buttons etc
        self.tree.get_widget("login_window").set_sensitive(False)
        self.tree.get_widget("username_entry").set_text(self.username)
        self.tree.get_widget("password_entry").set_text(self.password)
        self.tree.get_widget("login_error").set_text("Authenticating...")
        while gtk.events_pending():
            gtk.main_iteration(False)
        self.scrobbler = scrobbler.Scrobbler(self)
        if self.test_mode:
            server_response = "OK"
        else:
            server_response, msg = self.scrobbler.handshake()
        self.tree.get_widget("login_window").set_sensitive(True)
        if server_response == "OK":
            self.session_key = self.usersDB.get_session_key(self.username)
            return True
        else:
            self.authentication_error = msg
            return False
            
    
    def on_scrobble_clicked(self, widget):
        """Scrobbles tracks to last.fm"""
        #show scrobble dialog, if user has indicated in preferences
        if self.options.return_option("auto_time"):
            scr_time = self.scrobbler.return_total_time()
        elif self.options.return_option("use_default_time") == True:
            scr_time = self.options.return_option("scrobble_time")
        else:
            response = self.show_scrobble_dialog()
            if response is True:
                scr_time = self.tree.get_widget("scrobble_time_manual").get_value()
            else:
                return
        self.scrobble(scr_time)
        self.love_tracks()
        self.set_button_count()
                
    def scrobble(self, scr_time):
        self.write_info("Scrobbling started %s hours ago" % scr_time)
        self.scrobbler.set_scrobble_time(scr_time)
        scrobble_list = self.song_db.return_scrobble_list(self.options.return_scrobble_ordering())
        if self.scrobbler.submit_tracks(scrobble_list):
                self.song_db.delete_scrobbles('all')
        else:
            self.song_db.delete_scrobbles(self.scrobbler.deletion_ids)
        
        
    def love_tracks(self):
        """This should be called after scrobbling in order to love pending tracks
        I'm not sure if this is the best place for it since it may be time consuming
        if there is a whole lotta love... den den da da da da den"""
        if not self.session_key:
            return False
        love_cache = self.song_db.return_love_cache()
        loved = []
        if love_cache != []:
            webservice = webservices.LastfmWebService()
            self.write_info("Sending love...")
            progress_bar = ProgressBar(self.tree.get_widget("progressbar"), len(love_cache), 0)
            for item in love_cache:
                if webservice.love_track(item[1], item[2], self.session_key):
                    self.write_info(item[1] + " - " + item[2])
                    loved.append(item[0])
                    progress_bar.current_progress = len(loved)
            progress_bar.run_timer(finished=True)
            self.song_db.mark_as_love_sent(loved)
            self.write_info("Done.")
    
    
    def show_scrobble_dialog(self):
        self.tree.get_widget("scrobble_time_manual").set_value(self.options.return_option("scrobble_time"))
        response = self.tree.get_widget("scrobble_dialog").run()
        while gtk.events_pending():
            gtk.main_iteration(False)
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            self.tree.get_widget("scrobble_dialog").hide()
            return False
        else:
            return True
    
    def on_scrobble_time_entered_clicked(self, widget):
        self.tree.get_widget("scrobble_dialog").hide()
        
   
    def on_tracks_button_clicked(self, widget):
        classes = {"love" : songview.LovedWindow,
                   "ban" : songview.BannedWindow,
                   "cache" : songview.CacheWindow}
        new_window = classes[widget.name](self.GLADE[widget.name], self.song_db, self)


    def write_info(self, new_info, text_widget="Default",
                   new_line='\n', clear_buffer=False):
        """Writes data to the main window to let the user know what is going on"""
        if text_widget is "Default":
            text_widget = self.tree.get_widget("info")
        buffer = text_widget.get_buffer()
        if clear_buffer is True:
            buffer.set_text(new_info)
        else:
            #end = buffer.get_end_iter()
            buffer.insert_at_cursor(new_line + new_info)
        
        #scroll window to the end
        scroller = self.tree.get_widget("scrolledwindow")
        vadj = scroller.get_vadjustment()
        vadj.set_value(vadj.upper)
        vadj.emit("changed")
        while gtk.events_pending():
            gtk.main_iteration(False)




    #menu options
    def on_options_clicked(self, widget):
        for o in self.options.options_list:
            try:
                x = self.options.return_option(o)
                self.tree.get_widget(o).set_active(self.options.return_option(o))
            except AttributeError:
                self.tree.get_widget(o).set_value(self.options.return_option(o))
        #not sure why, but setting a value of 0 to a radio button doesnt seem to work
        #x = self.options.return_option("auto_time")
        #self.tree.get_widget("manual_time").set_active(not x)
        self.on_auto_time_toggled(None)
        response = self.options_window.show()
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            self.options_window.hide()
        
    def on_reset_db_clicked(self, widget):
        response = self.tree.get_widget("db_clear_dialog").run()
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            self.tree.get_widget("db_clear_dialog").hide()

    def db_clear_activate(self, widget):
        if widget.name == "apply_db_clear":
            os.remove(self.HOME_DIR + self.username + "DB")
            self.write_info("Database cleared")
            self.setup_user_session()
            self.tree.get_widget("options_window").hide()
        self.tree.get_widget("db_clear_dialog").hide()
    
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
                if remember_password is True:
                    self.usersDB.update_user(self.username, self.password)
                else:
                    self.usersDB.remove_user(self.username)
                self.setup_user_session()
            else:
                self.show_login_window()
                self.tree.get_widget("login_error").set_text(self.authentication_error)
    
    def setup_user_session(self):
        self.tree.get_widget("user").set_text(self.username)
        self.options = Options(self.username, self.usersDB)
        if not os.path.exists(self.HOME_DIR + self.username + 'DB'):
            self.write_info("User db doesn't exist, creating.")
            self.first_run = True
        else:
            self.first_run = False
        self.song_db = dbClass.lastfmDb(self.HOME_DIR + self.username + "DB", self.first_run)
        self.set_button_count()
        self.show_main_window()
        if self.options.return_option("startup_check") == True:
            self.on_check_device_clicked(None)

        
        
    def on_username_entry_insert_text(self, widget):
        """Check the user database on keypress to see if we have a match"""
        entry = self.tree.get_widget("username_entry").get_text()
        users = self.usersDB.get_users_like(entry)
        if len(users) is 1:
            self.tree.get_widget("username_entry").set_text(users[0][0])
            #we need to select the text after the cursor so the user can continue
            #writing without mistakes
    
    def on_password_entry_key_press_event(self, widget, key):
        if key.keyval == 65293:
            self.on_login_clicked(widget)
            
    def login_auto_completer(self):
        self.completion = gtk.EntryCompletion()
        self.completion.set_inline_completion(True)
        self.completion.set_popup_completion(False)
        self.tree.get_widget("username_entry").set_completion(self.completion)
        liststore = gtk.ListStore(str)
        self.completion.set_model(liststore)
        pixbufcell = gtk.CellRendererPixbuf()
        self.completion.pack_start(pixbufcell)
        self.completion.add_attribute(pixbufcell, 'pixbuf', 3)
        self.completion.set_text_column(0)
        users = self.usersDB.get_users(all=True)
        for user in users:
            liststore.append([user[0]])
    
    #this section deals with the OPTIONS WINDOW
    def on_options_window_destroy(self, widget, event=False):
        self.options_window.hide()
        return True
        
    
    def on_apply_options_clicked(self, widget):
        random = self.tree.get_widget("random").get_active()
        alpha = self.tree.get_widget("alphabetical").get_active()
        startup_check = self.tree.get_widget("startup_check").get_active()
        auto_scrobble = self.tree.get_widget("auto_scrobble").get_active()
        auto_time = self.tree.get_widget("auto_time").get_active()
        scrobble_time = self.tree.get_widget("scrobble_time").get_value()
        use_default_time = self.tree.get_widget("use_default_time").get_active()
        self.options.update_options(random, alpha,
                                    startup_check, auto_scrobble, auto_time,
                                    scrobble_time, use_default_time)
        self.options_window.hide()
        
    def on_auto_time_toggled(self, widget):
        active = self.tree.get_widget("auto_time").get_active()
        if active:    
            auto_active = False
        else:
            auto_active = True
        self.tree.get_widget("use_default_time").set_sensitive(auto_active)
        self.tree.get_widget("scrobble_time").set_sensitive(auto_active)
        
    
    #About Window
    def on_about_clicked(self, widget):
        response = self.tree.get_widget("about_dialog").run()
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            self.tree.get_widget("about_dialog").hide()

if __name__ == "__main__":
    mtp = MTPLastfmGTK(("Daniel",), "dev")
    gtk.main()