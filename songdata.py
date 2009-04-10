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
import time

import localisation
_ = localisation.set_get_text()

class SongData(object):
    
    def __init__(self, db, path, parent):
        self.db = db
        self.parent = parent
        self.ready_for_export = False
        self.required_data = {'Track ID:' : False, 'Title:' : False,
                              'Artist:' : False, 'Album:' : False,
                              'Track number:' : False, 'Duration:' : False,
                              'User rating:' : False, 'Use count:' :False}
        self.integer_types = ('Track ID:', 'Use count:',
                         'Duration:', 'User rating:')
        #for localisation we will have a separate list of required data
        #as it is used in other areas of the program
        self.required_data_locale = {'Track ID:' : _('Track ID'), 'Title:' : _('Title'),
                                     'Artist:' : _('Artist'), 'Album:' : _('Album'),
                                     'Track number:' : _('Track number'),
                                     'Duration:' : _('Duration'),
                                     'User rating:' : _('User rating'),
                                     'Use count:' : _('Playcount')}
        self.log = []
        self.song_count = 0
        self.error_count = 0
        
    def create_clean_dataset(self):
        for value in self.required_data:
            self.required_data[value] = False

    def check_new_data(self, data):
        key, value = self.split_data(data)
        #required data should be reset after each song
        #so if we have a non False value we should
        #append any missing data and export
        try:
            if self.required_data[key] is not False:
                if self.is_song():
                    self.append_missing_data()
                    self.set_rating()
                    self.db.add_new_data(self.required_data)
                    self.create_clean_dataset()
                    self.song_count += 1
                else:
                    self.log_data()
                    self.error_count += 1
                    self.create_clean_dataset()
            self.required_data[key] = self.add_new_data(key, value)
        except KeyError:
            pass
    
    def log_data(self):
        for key, value in self.required_data.iteritems():
            if value == False:
                self.required_data[key] = _("")
        self.log.append(dict(self.required_data))

    
    def add_new_data(self, key, value):
        if key in self.integer_types:
            i = value.find(' ')
            if i > 0:
                value = value[:i]
            value = int(value)
            if key == 'Duration:':
                value = value / 1000
            return value
        return unicode(value, 'utf-8')

    def is_song(self):
        """Check that all required songdata is accounted for"""
        for key, value in self.required_data.items():
            if value is False:
                if key == "Use count:" or key == "User rating:" or key == "Track number:" or key == "Album:":
                    continue
                else:
                    return False
        if self.required_data["Artist:"] == "Unknown artist":
            self.required_data["Artist:"] = ""
            return False
        return True
                

    def set_rating(self):
        """Set the rating to a last.fm friendly value"""
        values = { "" : u"", 99 : 'L', 1 : 'B' }
        try:
            new_rating = values[self.required_data['User rating:']]
        except KeyError:
            new_rating = ""
        self.required_data['User rating:'] = new_rating
  
    def append_missing_data(self):
        """The User rating and Use count may be missing.  If so, append
        them before export"""
        if self.required_data['User rating:'] is False:
            self.required_data['User rating:'] = ""
        if self.required_data['Use count:'] is False:
            self.required_data['Use count:'] = 0
        if self.required_data['Track number:'] is False:
            self.required_data['Track number:'] = ""
        if self.required_data['Album:'] is False:
            self.required_data['Album:'] = ""
        
    def split_data(self, data):
        """Splits the data into key, value"""
        i = data.find(":")
        key = data[0:i+1]
        value = data[i+2:-1]
        return key.strip(), value
