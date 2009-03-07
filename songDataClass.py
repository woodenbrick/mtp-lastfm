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

import string
import time
from logger import Logger

class SongData:
    def __init__(self):
        self.max = 8 #count of all possible song data
        self.required_data = ['Track ID', 'Title', 'Artist', 'Album', 'Track number', 
                             'Duration', 'Use Count', 'User rating']
        self.accepted_data_types = ('ISO MPEG-1 Audio Layer 3',)
        self.reset_values()
        self.log = Logger(name='Not added to scrobbling db', stream_log=False)

        
    def reset_values(self):
        self.song_data = []
        self.filetype_reached = False
        self.is_song = False
        self.ready_for_export = False
        
    def _is_song(self, data):
        for item in self.accepted_data_types:
            if data.__contains__(item):
                self.is_song = True
        
    def _is_data(self, data):
        """Returns true if the data submitted is data we want"""
        for item in self.required_data:
            if data.__contains__(item + ':'):
                return True
        if data.__contains__('Filetype:'):
            self.filetype_reached = True
            self._is_song(data)
        return False
        
    def _is_usecount(self, data):
        if data.__contains__('Use count:'):
            return True
        return False
        
    def _is_rating(self, data):
        if data.__contains__('User rating:'):
            return True
        return False
    
    
    def _clean_data(self, data):
        """Strips unneeded info"""
        index = data.find(":")
        clean_data = data[index+2:-1]
        if self._is_rating(data):
            index = clean_data.find(' ')
            clean_data = clean_data[:index]
            if clean_data == '1':
                clean_data = 'B'
            elif clean_data == '99':
                clean_data = 'L'
            else:
                clean_data = ''
        return clean_data
    
    def _get_key(self, data):
        """returns the key (eg. Album) for a string"""
        key = string.split(data, ':')[0][:-1]
        return key
        
    def new_data(self, new_data):
        """Needs to find out what data it is and assign 
        it to the correct variable"""
        if self.filetype_reached == True:
            #check if this line is usecount if not we need to append
            if self._is_rating(new_data):
                self.song_data.append(self._clean_data(new_data))
            else:
                self.song_data.append("''")
            if self._is_usecount(new_data):
                self.song_data.append(self._clean_data(new_data))
            else:
                self.song_data.append('0 times')
            self.export_data()
            if self.ready_for_export == False:
                self.new_data(new_data)
                
        elif self._is_data(new_data):
            clean = self._clean_data(new_data)
            self.song_data.append(clean)
        else:
            pass
            
        
    def check_if_full(self):
        """Returns true if all songdata is available. Note that Use Count wont exist
        if the song has never been played"""
        if len(self.song_data) == self.max:
            return True
        return False
        
        
    def export_data(self):
        """Sends song data to database"""
        #trim seconds and usecount before export
        if self.is_song == True and self.check_if_full() and self.song_data[5] > 30:
            self._trim_export_data()
            self.ready_for_export = True
        else:
            data = '\n'.join(self.song_data) 
            self.log.logger.warn(data)
            self.reset_values()
        
    
    def _trim_export_data(self):
        self.trackid = int(self.song_data[0])
        self.title = self.song_data[1]
        self.artist = self.song_data[2]
        self.album = self.song_data[3]
        self.tracknumber = int(self.song_data[4])
        self.duration = int(string.split(self.song_data[5], ' ')[0]) / 1000
        self.rating = self.song_data[6]
        self.usecount = int(string.split(self.song_data[7], ' ')[0])
