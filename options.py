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

class Options:
    def __init__(self, username, db):
        self.options_list = ("random", "alphabetical", "startup_check",
                        "auto_scrobble", "auto_time", "scrobble_time", "use_default_time")
        self.db = db
        self.username = username
        self.reset_default()
        self.reset_options()
    
    def update_options(self, *args):
        self.db.update_options(self.username, *args)
        self.reset_options()
    
    def reset_options(self):
        options = self.db.retrieve_options(self.username)
        if options is None:
            self.username = "default"
            options = self.db.retrieve_options(self.username)
        self.dic_options = self.create_option_dic(options)
        
    def return_scrobble_ordering(self):
        if self.return_option("random") == True:
            return "RANDOM()"
        else:
            return "songs.artist"
    
    
    def reset_default(self):
        self.db.reset_default_user()
        
    def create_option_dic(self, options):
        dic = {}
        for o in range(0, len(self.options_list)):
            dic[self.options_list[o]] = options[o]
        return dic
    
    def return_option(self, option_name):
        return self.dic_options[option_name]
        