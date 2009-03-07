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

from logger import Logger


class SongData(object):
    def __init__(self, db):
        self.db = db
        self.create_clean_dataset()
        self.ready_for_export = False
        integer_types = ('Track ID:', 'Track number:', 'Use Count:',
                         'Duration', 'User rating:')
        self.log = Logger(name='Not added to scrobbling db', stream_log=False,
                          file_log_name='~/.mtp-lastfm/import_errors.log')
        
    def create_clean_dataset(self):
        self.required_data = {'Track ID:' : False, 'Title:' : False,
                              'Artist:' : False, 'Album:' : False,
                              'Track number:' : False, 'Duration:' : False,
                              'User rating:' : False, 'Use Count:' :False}

    def check_new_data(self, data):
        key, value = self._split_data(data)
        #required data should be reset after each song
        #so if we have a non False value we should
        #append any missing data and export
        if self.required_data[key] is not False:
            if self.is_song():
                self.append_missing_data()
                self.set_rating()
                self.db.add_new_data(self.required_data)
            else:
                self.log.logger.warn(self.required_data)
            self.create_clean_dataset()
        #we can now create the new dataset
        self.required_data[key] = add_new_data(key, value)
        
    def add_new_data(self, key, value):
        if key in self.integer_types:
            i = value.find(' ')
            if i is not 0:
                value = value[:i]
            value = int(value)
            if key == 'Duration:':
                value = value / 1000
            return value
        return value

    def set_rating(self):
        """Set the rating to a last.fm friendly value"""
        values = { "''" : "''", 99 : 'L', 1 : 'B' }
        try:
            new_rating = values[self.required_data['User rating:']]
        except KeyError:
            new_rating = "''"
        self.required_data['User rating:'] = new_rating
  
    def append_missing_data(self):
        """The User rating and Use count may be missing.  If so, append
        them before export"""
        if self.required_data['User rating:'] is False:
            self.required_data['User rating:'] = "''"
        if self.required_data['Use Count:'] is False:
            self.required_data['Use Count:'] = 0
        
    def split_data(self, data):
        """Splits the data into key, value"""
        i = data.find(":")
        key = data[0:i]
        value = data[i+2:-1]
        return key, value