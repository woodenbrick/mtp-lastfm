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

import hashlib
import time
import urllib
import gtk
import pygtk

import xml.etree.ElementTree as ET

import string
import dbClass
import webbrowser
from progressbar import ProgressBar
from httprequest import HttpRequest

import localisation
_ = localisation.set_get_text()
_pl = localisation.set_get_text_plural()

class Scrobbler:
    
    def __init__(self, parent):
        self.user = parent.username
        self.password = parent.password
        self.parent = parent
        self.client = 'mtl'
        self.version = '1.0'
        self.url = "http://post.audioscrobbler.com:80"
        self.deletion_ids = []
        self.scrobble_count = 0
        
    def set_scrobble_time(self, time):
        self.scrobble_time = int(time * 3600)
        
    def return_total_time(self):
        """Gets the total amount of time for all songs to be scrobbled"""
        list = self.parent.song_db.return_scrobble_list()
        total_dur = 0
        for duration in list:
            total_dur += duration[3]
        return round(total_dur / 3600.0, 2)
        
    def handshake(self):
        self.timestamp = self.create_timestamp()
        self.authentication_code = self.create_authentication_code()
        self.url += r"/?" + self.encode_url()
        
        req = HttpRequest(url=self.url, timeout=10)
        success, response = req.connect()
           
        if success:
            self.session_id = response[1]
            self.submission_url = response[3]
            
        msg = req.handshake_response(response[0])
        return response[0], msg
    
    


    def submit_tracks(self, c):
        """Takes c, a cursor object with scrobble data and tries to submit it to last.fm"""
        past_time = int(time.time() - self.scrobble_time)
        progress_bar = ProgressBar(self.parent.tree.get_widget("progressbar"))
        progress_bar.set_vars(self.parent.song_db.scrobble_counter, 0)
        progress_bar.start()
        while True:
            cache = c.fetchmany(50)
            if len(cache) == 0:
                progress_bar.stop()
                break
            else:
                self.parent.write_info(_pl('Preparing %(num)d track for scrobbling',
                                         'Preparing %(num)d tracks for scrobbling',
                                         len(cache)) % {'num' : len(cache)})
                self.scrobble_count += len(cache)
                progress_bar.current_progress += len(cache)
                while gtk.events_pending():
                    gtk.main_iteration()
                
                #s=<session_id>  The Session ID returned by the handshake. Required.
                #a[0]=<artist>  The artist name. Required.
                #t[0]=<track>   The track title. Required.
                #i[0]=<time>    The time the track started playing, UNIX timestamp.
                #o[0]=<source>  Put P for this value
                #r[0]=<rating>  Blank or dont use(for now)
                #l[0]=<secs>    The length of the track in seconds. 
                #b[0]=<album>   The album title, or an empty string if not known.
                #n[0]=<tracknumber>The position of the track on the album, or empty.
                #m[0]=music brainz identifier, leave blank
                
                #create dictionary the size of the cache and fill in defaults
                param = "a t l b n r".split(' ')
                post_values = {}
                self.del_ids = []
                
                index = 0
                for track in cache:
                    str_index = "[" + str(index) + "]"
                    for i in range(0, len(param)):
                        str_param = str(param[i]) + str_index
                        post_values[str_param] = track[i+1]
                        #work out play time based on track length
                        if param[i] == "l":
                            past_time += track[i+1]
                            post_values["i" + str_index] = past_time
                            
                    post_values["m" + str_index] = u""
                    post_values["o" + str_index] = u"P"
                    self.del_ids.append(track[0])
                    index += 1
                        
                post_values["s"] = self.session_id
                post_values = urllib.urlencode(post_values)
                self.parent.write_info(_("Sending tracks, waiting for reply..."))
                if not self._send_post(post_values):
                    return False
                else:
                    self.parent.write_info(_("OK"), new_line=" ")
        #if all songs are scrobbled with ok response:
        if self.scrobble_count is not 0:
            self.parent.write_info(_pl("Scrobbled %(num)d track",
                                     "Scrobbled %(num)d tracks",
                                     self.scrobble_count) % {"num" : self.scrobble_count})
        else:
            self.parent.write_info(_("Nothing to scrobble."))
        return True

  
    def _send_post(self, post_values):
        req = HttpRequest(url=self.submission_url, data=post_values, timeout=10)
        success, msg = req.connect()
        if success:
            self.deletion_ids.extend(self.del_ids)    
            return True
        else:
            self.parent.write_info(_("There was an error sending data to last.fm:") +
                                   "\n" + "\n".join(msg))
            return False
   
    def encode_url(self):
        u = urllib.urlencode({
            "hs":"true",
            "p":"1.2",
            "c":self.client,
            "v":self.version,
            "u":self.user,
            "t":self.timestamp,
            "a":self.authentication_code})
        return u
    
    def create_authentication_code(self):
        code = hashlib.md5(self.password + self.timestamp).hexdigest()
        return code
    
    def create_timestamp(self):
        stamp = str(int(time.time()))
        return stamp

