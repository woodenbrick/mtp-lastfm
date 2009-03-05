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

class Scrobbler:
    
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.client = 'tst'
        self.version = '1.0'
        self.url = "http://post.audioscrobbler.com:80"
        self.deletion_ids = []
        self.scrobble_count = 0
        self.log = Logger(name='scrobbling', stream_log_level=2)
        
    def set_scrobble_time(self, time):
        self.scrobble_time = int(time * 3600)
        
    
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
            msg = 'User authenticated.'
            self.session_id = conn.readline()[:-1]
            self.now_playing_url = conn.readline().strip #not used at this time
            self.submission_url = conn.readline()[:-1]
        if self.server_response.startswith("FAILED"):
            responses['FAILED'] = string.split(self.server_response, ' ')[1:]
        
        return self.server_response, responses[self.server_response]
    
    


    def submit_tracks(self, c):
        """Takes c, a cursor object with scrobble data and tries to submit it to last.fm"""

        past_time = int(time.time() - self.scrobble_time)
        while True:
            cache = c.fetchmany(50)
            if len(cache) == 0:
                break
            else:
                self.scrobble_count += len(cache)
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
                full_list = [[], [], [], [], [], [], []]
                size = len(cache)
                for track in cache:
                    for index in range(0, len(full_list)):
                        song_data_item = track[index]
                        try:
                            #this is to avoid a unicode to ascii error,
                            #which occours when we try to urlencode accented characters
                            #(umlauts etc.)
                            song_data_item = song_data_item.encode('UTF-8')
                        except AttributeError:
                            #cannot encode integers
                            pass
                        
                        full_list[index].append(song_data_item)
                #remove row ID's which will track which items in scrobble
                #list require deletions
                self.del_ids = full_list.pop(0)
                #append extra data to full_list, time, source, musicbrainz tags
                while len(full_list) < 9:
                    full_list.append([])
                for extra in range(0, len(cache)):
                    #append time, use l to work out
                    length = full_list[2][extra]
                    past_time += int(length)
                    full_list[6].append(past_time)
                    #append source (always P)
                    full_list[7].append(u"P")
                    #empty strings for music brain tag
                    full_list[8].append(u"")
                    
                post_values = { "s" : self.session_id }
                for i in range(0, size):
                    dic = self.get_dic_value(i)
                    for j in range (0, len(dic)): #haha!
                        post_values[dic[j]] = full_list[j][i]
                post_values = urllib.urlencode(post_values)
                if not self._send_post(post_values):
                    self.log.logger.critical('Error posting to last.fm')
                    return False
        #if all songs are scrobbled with ok response: 
        return True   
    def get_dic_value(self, i):
        """Returns a list of dictionary keys for a specified index"""
        values = "atlbnriom"
        list = []
        for v in values:
            list.append("%s[%d]" % (v, i))
        return list
        
    def _send_post(self, post_values):
        req = urllib2.Request(url=self.submission_url, data=post_values)
        try:
            url_handle = urllib2.urlopen(req)
            response = url_handle.readline().strip()
        except urllib2.URLError:
            response = 'Connection Refused, please try again'
        except httplib.BadStatusLine:
            response = 'Bad Status Line'
        if response == 'OK':
            self.log.logger.info('Scrobbled %d songs' % self.scrobble_count)
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

