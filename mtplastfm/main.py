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
import sys
import os
import re
import hashlib
import gtk
import pygtk
import urllib
import gtk.glade
import threading
import Queue
import webbrowser
gtk.gdk.threads_init()
import time
pygtk.require("2.0")

import dbClass
import scrobbler
import songview
import webservices
from progressbar import ProgressBar
from options import Options
from httprequest import HttpRequest
from cmod import mtpconnect

import localisation
_ = localisation.set_get_text()
_pl = localisation.set_get_text_plural()

#these are returned after an attempted connection to an MTP device
mtp_error_strings = {0 : _("Successfully connected"),
                     1 : _("General error"),
                     2 : _("PTP Layer Error"),
                     3 : _("USB Layer Error"),
                     4 : _("Memory Allocation Error"),
                     5 : _("No device attached"),
                     6 : _("Storage full"),
                     7 : _("Problem connecting"),
                     8 : _("Connection cancelled")}

mtp_invalid_file_strings = {1 : _("Invalid filetype"),
                            2 : _("Invalid artist"),
                            3 : _("Invalid title")}


class MTPLastfmGTK:
    def __init__(self, author, version, home, glade, test_mode=False):
        self.test_mode = test_mode
        self.author = author
        self.version = version
        self.HOME_DIR = home
        self.GLADE = glade

        self.tree = gtk.glade.XML(self.GLADE['gui'])
        self.tree.signal_autoconnect(self)

        self.main_window = self.tree.get_widget("main_window")
        self.options_window = self.tree.get_widget("options_window")
        self.login_window = self.tree.get_widget("login_window")
        self.progress_bar = ProgressBar(self.tree.get_widget("progressbar"))
        
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
        self.main_window.show()
        self.tree.get_widget("info").get_window(
            gtk.TEXT_WINDOW_TEXT).set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))
        self.set_user_image()
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
        #open dblog
        log = open(self.HOME_DIR + "db.log", "w")
        log.write(_("Tracks that recently failed a validity check:\n"))
        #disable button as a double click will cause a panic
        self.tree.get_widget("check_device").set_sensitive(False)
        self.write_info(_("Connecting to MTP device"))
        conn_status = mtpconnect.open_device()
        if conn_status != 0:
            self.write_info(mtp_error_strings[conn_status])
            self.tree.get_widget("check_device").set_sensitive(True)
            return
        self.tree.get_widget("send_comp_info").set_sensitive(True)
        self.stats = {"manufacturer" : mtpconnect.get_manufacturer(),
                     "model" : mtpconnect.get_model(),
                     "name" : mtpconnect.get_friendly_name()}
        self.write_info(_("Successfully connected to %(name)s %(model)s" % self.stats))
        current_track = mtpconnect.get_tracks()
        track_count = mtpconnect.get_track_count()
        invalid_track_count = 0
        self.progress_bar.set_vars(max_value=track_count)
        self.write_info(_("%s items found on device, cross checking with local database..." % track_count))
        self.progress_bar.start()
        #reset song counter to 0 so we know how many new scrobbles were added this time
        #in case there were some pending already
        self.song_db.new_scrobble_count = 0
        while current_track is not None:
            if mtpconnect.is_valid_track() == 0:
                #build a songdic that matches old implementation
                song = {"id" : mtpconnect.get_item_id(),
                        "artist" : mtpconnect.get_artist(),
                        "title" : mtpconnect.get_title(),
                        "tracknumber" : mtpconnect.get_track_number(),
                        "rating" : mtpconnect.get_rating(),
                        "album" : mtpconnect.get_album(),
                        "duration" : mtpconnect.get_duration(),
                        "usecount" : mtpconnect.get_usecount()}
                self.song_db.add_new_data(song)
            else:
                invalid_track_count += 1
                self.log_error(log)
            current_track = mtpconnect.next_track()
            self.progress_bar.current_progress += 1
            if self.progress_bar.current_progress % 20 == 0 or self.progress_bar.current_progress > track_count - 20:
                self.progress_bar.progress_bar.set_text(song['artist'])
                self.tree.get_widget("cache_label").set_text("(%s)" % self.song_db.scrobble_counter)            
            if self.progress_bar.current_progress == track_count:
                self.progress_bar.set_vars(pulse_mode=True, text=_("Closing device"))
            while gtk.events_pending():
                gtk.main_iteration()
        if track_count == 0:
            self.write_info(_("No tracks were found on your device."))
        if self.song_db.new_scrobble_count != 0:
            self.write_info(_("Found %s new tracks for scrobbling" % self.song_db.new_scrobble_count))
        mtpconnect.close_device()
        self.progress_bar.stop()
        if invalid_track_count > 0:
            self.create_log_button(invalid_track_count)
            self.tree.get_widget("log_menu").set_sensitive(True)
        else:
            self.tree.get_widget("log_menu").set_sensitive(False)
        log.close()
        self.song_db.reset_scrobble_counter()
        self.set_button_count()
        self.tree.get_widget("check_device").set_sensitive(True)
        if self.options.return_option("auto_scrobble") == True:
            self.on_scrobble_clicked(None)
        if not self.usersDB.has_asked_for_stats(self.username, self.stats):
            self.open_program_works_dialog(None)
            self.usersDB.asked_for_stats(self.username, self.stats)


    def create_log_button(self, error_count):
        self.write_info(_pl("%(num)d item was not added to your song database.\n",
                            "%(num)d items were not added to your song database.\n",
                            error_count) % {"num" : error_count})
        buffer = self.tree.get_widget("info").get_buffer()
        iter = buffer.get_end_iter()
        anchor = buffer.create_child_anchor(iter)
        button = gtk.Button(label=None, stock="gtk-info")
        button.show()
        self.tree.get_widget("info").add_child_at_anchor(button, anchor)
        button.connect("clicked", self.show_error_details, None)

    def log_error(self, log):
        log.write("%s: %s\nID: %s\n%s: %s\n%s: %s\n\n" %
            (_("Reason"), mtp_invalid_file_strings[mtpconnect.is_valid_track()],
             mtpconnect.get_item_id(), _("Title"), str(mtpconnect.get_title()),
             _("Artist"), str(mtpconnect.get_artist())))
             
    def show_error_details(self, *args):
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
                "Pending love"],
            
            "ban" :
                [len(self.song_db.return_tracks("B").fetchall()),
                "Banned tracks"],
                
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
            #set the song count for the cache button
            #not sure yet how to change the label on a menu item
            try:
                self.tree.get_widget(value[1]).set_text(text)
            except:
                pass
            self.tree.get_widget(key).set_sensitive(sensitivity)
   
    def authenticate_user(self):
        """This authenticates the user with last.fm ie. The Handshake"""
        #disable all buttons etc
        self.tree.get_widget("vbox7").set_sensitive(False)
        self.tree.get_widget("username_entry").set_text(self.username)
        self.tree.get_widget("password_entry").set_text(self.password)
        self.tree.get_widget("login_error").set_text(_("Authenticating..."))
        while gtk.events_pending():
            gtk.main_iteration(False)
        self.scrobbler = scrobbler.Scrobbler(self)
        if self.test_mode:
            server_response = "OK"
            msg = "This is the test version, scrobbling is disabled"
        else:
            server_response, msg = self.scrobbler.handshake()
        self.tree.get_widget("vbox7").set_sensitive(True)
        if server_response == "OK":
            self.write_info(msg, clear_buffer=True)
            self.session_key = self.usersDB.get_session_key(self.username)
            return True
        else:
            self.authentication_error = msg.reason[1]
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
        self.write_info(_("Scrobbling started %s hours ago") % scr_time)
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
            self.write_info(_("Sending love..."))
            self.progress_bar.set_vars(len(love_cache), 0)
            self.progress_bar.start()
            for item in love_cache:
                self.write_info(item[1] + " - " + item[2])
                response = webservice.love_track(item[1], item[2], self.session_key)
                if response == "ok":
                    self.write_info(_("Ok."), new_line=" ")
                    loved.append(item[0])
                    self.progress_bar.current_progress = len(loved)
                    while gtk.events_pending():
                        gtk.main_iteration()
                else:
                    self.write_info(response)
            self.progress_bar.delayed_stop(300)
            self.song_db.mark_as_love_sent(loved)
            self.write_info(_("Done."))
    
    
    def show_scrobble_dialog(self):
        self.tree.get_widget("scrobble_time_manual").set_value(
            self.options.return_option("scrobble_time"))
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
        new_window = classes[widget.name](self.song_db, self)


    def write_info(self, new_info, text_widget="Default",
                   new_line='\n', clear_buffer=False):
        """Writes data to the main window to let the user know what is going on"""
        if text_widget is "Default":
            text_widget = self.tree.get_widget("info")
        buffer = text_widget.get_buffer()
        if clear_buffer is True:
            buffer.set_text(new_info)
        else:
            end = buffer.get_end_iter()
            buffer.insert(end, new_line + new_info)
        
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
        self.on_auto_time_toggled(None)
        #check if authenticated
        if self.session_key:
            self.tree.get_widget("auth_label").set_text(_("User authenticated"))
            self.tree.get_widget("authenticate").hide()
        self.options_window.show()

        
    def on_reset_db_clicked(self, widget):
        response = self.tree.get_widget("db_clear_dialog").run()
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            self.tree.get_widget("db_clear_dialog").hide()

    def db_clear_activate(self, widget):
        if widget.name == "apply_db_clear":
            os.remove(self.HOME_DIR + self.username + "DB")
            self.write_info(_("Database cleared"))
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
            login_error.set_text(_("Error: Please enter a username and password"))
        else:
            if not re.findall(r"^([a-fA-F\d]{32})$", self.password):
                self.password = hashlib.md5(self.password).hexdigest()
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
        self.tree.get_widget("user").set_markup("<b>%s</b>" % self.username)
        self.options = Options(self.username, self.usersDB)
        if not os.path.exists(self.HOME_DIR + self.username + 'DB'):
            self.write_info(_("User database doesn't exist, creating."))
            self.first_run = True
        else:
            self.first_run = False
        self.song_db = dbClass.lastfmDb(self.HOME_DIR + self.username + "DB",
                                        self.first_run)
        self.set_button_count()
        self.show_main_window()
        if self.options.return_option("startup_check") == True:
            self.on_check_device_clicked(None)
        
    
    def set_user_image(self):
        webservice = webservices.LastfmWebService()
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=%s&api_key=%s"
        request = HttpRequest(url=url % (self.username, webservice.api_key), timeout=10)
        msg = request.connect(xml=True)
        image_url = webservice.parse_xml(msg, "image")
        if image_url is None:
            return
        if not os.path.exists(self.HOME_DIR + os.path.basename(image_url)):
            request = HttpRequest(image_url)
            request.retrieve(image_url, self.HOME_DIR + os.path.basename(image_url),
                             self.tree.get_widget("user_thumb"))
        else:
            image = gtk.gdk.pixbuf_new_from_file_at_size(self.HOME_DIR +
                                                         os.path.basename(image_url),
                                                         100, 40)
            self.tree.get_widget("user_thumb").set_from_pixbuf(image)
            
    def on_username_entry_insert_text(self, widget):
        """Check the user database on keypress to see if we have a match"""
        entry = self.tree.get_widget("username_entry").get_text()
        users = self.usersDB.get_users_like(entry)
        if len(users) is 1:
            self.tree.get_widget("username_entry").set_text(users[0][0])

    
    def on_password_entry_key_press_event(self, widget, key):
        #this logs in the user if they press Enter from the password box
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
        
    def on_authenticate_clicked(self, widget):
        """This is the button in the options menu"""
        text = _("Please authenticate MTP-Lastfm in your web browser.  \
                 This is required if you wish to love/tag tracks.  \
                 After the authentication is complete click OK")
        message = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO,
                                    gtk.BUTTONS_OK_CANCEL, text)
        webservice = webservices.LastfmWebService()
        token = webservice.request_session_token()
        webservice.request_authorisation(token)
        resp = message.run()
        message.destroy()
        if resp == gtk.RESPONSE_OK:
            valid, session_key = webservice.create_web_service_session(token)
            if valid is True:
                self.usersDB.add_key(self.username, session_key)
                self.tree.get_widget("auth_label").set_text(_("User authenticated"))
                self.tree.get_widget("authenticate").hide()
                self.session_key = session_key
                text = _("Authentication complete")
            else:
                self.tree.get_widget("auth_label").set_text(session_key)
                text = session_key
            result = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO,
                                    gtk.BUTTONS_OK, text)
            result.run()
            result.destroy()
              
              
    def on_about_clicked(self, widget):
        response = self.tree.get_widget("about_dialog").run()
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            self.tree.get_widget("about_dialog").hide()
            
    def open_website(self, widget):
        buttons = {"user_button" : "http://last.fm/user/%s" % self.username,
                   "report_bug" : "https://bugs.launchpad.net/mtp-lastfm"}
        webbrowser.open_new_tab(buttons[widget.name])
        
    def open_program_works_dialog(self, widget):
        #check if user has scrobbles pending, if they do then software works
        #no scrobbles would indicate that it doesn't (though this is not certain
        #as users may not have listened to any tracks on device
        if self.song_db.scrobble_counter > 0:
            comp_str = _("MTP-Lastfm has %s pending scrobbles from your device and "
            "is considered compatible." % self.song_db.scrobble_counter)
            self.tree.get_widget("radio_prog_work").set_active(True)
        elif self.song_db.cursor.execute(
            """select * from songs where usecount > 0""").fetchone() is not None:
            comp_str = _("MTP-Lasfm has previously scrobbled tracks from your device and "
            "is considered compatible.")
            self.tree.get_widget("radio_prog_work").set_active(True)
        else:
            comp_str = _("MTP-Lastfm didn't find any played songs on your device. "
            "If you have definitely listened to tracks before connecting, then "
            "please mark as incompatible.")
            self.tree.get_widget("radio_prog_not_work").set_active(False)
        self.tree.get_widget("compatibility_msg").set_text(comp_str)
        self.tree.get_widget("data_to_be_submitted").set_markup(_(
        "The following data will be submitted:\n"
        "Manufacturer: <b>%(manufacturer)s</b>\nModel: <b>%(model)s</b>"
        "\nName: <b>%(name)s</b>\nLast.fm username: " %
        self.stats) + "<b>%s</b>\n\n" % self.username)
        self.tree.get_widget("send_info").show()

    def on_program_works_submit(self, widget):
        #send to server
        start, end = self.tree.get_widget("comment").get_buffer().get_bounds()
        data = {"os" : self.tree.get_widget("os").get_text(),
                "comment": self.tree.get_widget("comment").get_buffer().get_text(start, end),
                "username" : self.username,
                "not_working" : 0 if
                self.tree.get_widget("radio_prog_work").get_active() else 1}
        data.update(self.stats)
        data = urllib.urlencode(data)
        response = urllib.urlopen("http://mtp-lastfm.appspot.com/api/add", data)
        success = response.read()
        if success == "OK\n":
            self.write_info(_("Compatibility information submitted."))
        else:
            self.write_info(_("An error occured during submission"))
            sys.stderr.write(success)
        self.tree.get_widget("send_info").hide()
    
    def on_program_works_cancel(self, widget):
        self.tree.get_widget("send_info").hide()
    
    def on_program_works_destroy(self, widget):
        self.tree.get_widget("send_info").hide()
        return True
    
    def has_issue(self, widget):
        webbrowser.open_new_tab("http://mtp-lastfm.appspot.com/device/all")

