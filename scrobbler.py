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
import md5
import time
import urllib
import urllib2

import xml.etree.ElementTree as ET

import string
import dbClass
import webbrowser
from logger import Logger
from progressbar import ProgressBar

class Scrobbler:
    
    def __init__(self, parent):
        self.user = parent.username
        self.password = parent.password
        self.parent = parent
        self.client = 'tst'
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
        try:
            conn = urllib2.urlopen(self.url)
            self.server_response = conn.readline().strip()
        except urllib2.URLError:
            return 'NO INTERNET', "Couldn't find Last.fm server"
        except httplib.BadStatusLine, msg:
            return 'No Server Response', msg
        
        responses = {
            "OK" : "User authenticated",
            "BADAUTH" : "Username or password incorrect, please reset",
            "BANNED" : """This scrobbling client has been banned from submission,
                  please notify the developer""",
            "BADTIME" : "Timestamp is incorrect, please check your clock settings",
            "FAILED" : "Failed"
        }
           
        if self.server_response == 'OK':
            self.session_id = conn.readline()[:-1]
            self.now_playing_url = conn.readline().strip #not used at this time
            self.submission_url = conn.readline()[:-1]
        if self.server_response.startswith("FAILED"):
            responses['FAILED'] = string.split(self.server_response, ' ')[1:]
        self.parent.write_info(responses[self.server_response])
        return self.server_response, responses[self.server_response]
    
    


    def submit_tracks(self, c):
        """Takes c, a cursor object with scrobble data and tries to submit it to last.fm"""
        past_time = int(time.time() - self.scrobble_time)
        progress_bar = ProgressBar(self.parent.tree.get_widget("progressbar"),
                                   self.parent.song_db.scrobble_counter, 0)
        while True:
            cache = c.fetchmany(50)
            if len(cache) == 0:
                progress_bar.run_timer(finished=True)
                break
            else:
                self.parent.write_info('Preparing %d tracks for scrobbling' % len(cache))
                self.scrobble_count += len(cache)
                progress_bar.current_progress = self.scrobble_count
                
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
                self.parent.write_info("Sending tracks, waiting for reply...")
                if not self._send_post(post_values):
                    return False
        #if all songs are scrobbled with ok response: 
        return True

  
    def _send_post(self, post_values):
        req = urllib2.Request(url=self.submission_url, data=post_values)
        try:
            url_handle = urllib2.urlopen(req)
            response = url_handle.readline().strip()
        except urllib2.URLError:
            response = 'Connection Refused, please try again'
        except httplib.BadStatusLine:
            response = 'Bad Status Line'
        self.parent.write_info(response, new_line=' ')
        if response == 'OK':
            self.deletion_ids.extend(self.del_ids)    
            return True
        else:
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
        code = md5.new(self.password + self.timestamp).hexdigest()
        return code
    
    def create_timestamp(self):
        stamp = str(int(time.time()))
        return stamp

