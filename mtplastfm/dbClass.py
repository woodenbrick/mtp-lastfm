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
import sqlite3
import getpass


class lastfmDb_Users:
    def __init__(self, path):
        path = os.path.join(path, "usersDB")
        if not os.path.exists(path):
            self.create_new_database(path)    
        self.db = sqlite3.Connection(path)
        self.cursor = self.db.cursor()
    
    def create_new_database(self, path):
        connection = sqlite3.Connection(path)
        query = ['''CREATE TABLE IF NOT EXISTS `users` (
        `username` varchar(100) NOT NULL,
        `password` varchar(255) NOT NULL,
        `time` integer(20) NOT NULL
        )''',
        '''CREATE TABLE IF NOT EXISTS `sessionkeys` (
        `username` varchar(100) NOT NULL,
        `sessionkey` varchar(255) DEFAULT NULL
        )''',
        '''CREATE TABLE IF NOT EXISTS `options` (
        `username` varchar(100) NOT NULL,
        `scrobble_order_random` boolean DEFAULT 1,
        `scrobble_order_alpha` boolean DEFAULT 0,
        `connect_on_startup` boolean DEFAULT 0,
        `auto_scrobble` boolean DEFAULT 0,
        `auto_time` boolean DEFAULT 0,
        `scrobble_time` integer(3) DEFAULT 8,
        `use_default_time` boolean DEFAULT 0
        )''',
        ]
        
        cursor = connection.cursor()
        for q in query:
            cursor.execute(q)
        connection.commit()
        connection.close()
        
    def get_users(self, all=False):
        """Returns last user who logged in and chose to remember their password
        set all to true to get all users"""
        self.cursor.execute("SELECT * FROM users ORDER BY time DESC")
        if all is False:
            current_user = self.cursor.fetchone()
            return current_user
        else:
            return self.cursor.fetchall()
        
    def get_average_connection_time(self, user):
        """Returns the average of the users previous MTP connection times"""
        try:
            self.cursor.execute("SELECT conn_count, total_time from connection_timer WHERE username=?", (user,))
        except sqlite3.OperationalError:
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS `connection_timer` (
                                `username` varchar(100) NOT NULL,
                                `conn_count` integer(5) DEFAULT 0,
                                `total_time` integer(10) DEFAULT 0)""")
            self.db.commit()
            return self.get_average_connection_time(user)
        
        avg = self.cursor.fetchone()
        if avg is None:
            self.cursor.execute("""INSERT INTO connection_timer (username) VALUES (?)""", (user,))
            self.db.commit()
            avg = (0, 0)
        return avg
    
    
    def update_connection_time(self, user, count, total):
        total = round(total)
        self.cursor.execute("""UPDATE connection_timer set conn_count=?,
                            total_time=? WHERE username=?""", (count, total, user))
        self.db.commit()

   
    def get_session_key(self, user):
        """Return the session key for user, or False if no key exists
        This is user to love submissions"""
        self.cursor.execute("SELECT sessionkey from sessionkeys WHERE username=?", (user,))
        key = self.cursor.fetchone()
        if key is None:
            return False
        else:
            return key[0]
        
    def add_key(self, user, key):
        self.cursor.execute("INSERT into sessionkeys (username, sessionkey) VALUES (?, ?)"
                            , (user, key))
        self.db.commit()
    
    
    def get_users_like(self, name):
        """Returns users who have a name starting with the give string"""
        name = name + "%"
        self.cursor.execute("SELECT username FROM users WHERE username LIKE ?", (name,))
        return self.cursor.fetchall()
        
    def user_exists(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        row = self.cursor.fetchone()
        if row is None:
            return False
        else:
            return row
    
    def add_session_key(self, key, username):
        self.cursor.execute("update users set sessionkey=? where username=?", (key, username))
        self.db.commit()
    
    def update_user(self, username, password):
        import time
        current_time = time.time()
        if self.user_exists(username):
            query = "update users set password='%s', time=%d where username='%s'" % (password, current_time, username)
        else:
            query = "insert into users (username, password, time) values ('%s', '%s', %d)" % (username, password, current_time)
            self.cursor.execute("insert into options (username) values (?)", (username,))
        self.cursor.execute(query)
        self.db.commit()

    def remove_user(self, username):
        self.cursor.execute("delete from users where username=?", (username,))
        self.cursor.execute("delete from options where username=?", (username,))
        self.db.commit()
        
    def update_options(self, username, *args):
        query = """update options set scrobble_order_random=%d, scrobble_order_alpha=%d,
        connect_on_startup=%d, auto_scrobble=%d, auto_time=%d, scrobble_time=%d,
        use_default_time=%d WHERE username='%s'""" % (args[0], args[1], args[2], args[3], args[4], args[5], args[6], username)
        self.cursor.execute(query)
        self.db.commit()
    
    def retrieve_options(self, username):
        self.cursor.execute("""select scrobble_order_random,
                            scrobble_order_alpha, connect_on_startup, 
                        auto_scrobble, auto_time, scrobble_time, use_default_time from
        options where username=?""", (username,))
        return self.cursor.fetchone()
    
    def reset_default_user(self):
        '''reset default user when program closes'''
        self.cursor.execute("""delete from options where username='default'""")
        self.cursor.execute("""insert into options (username) values ('default')""")
        self.db.commit()


    
class lastfmDb:
    def __init__(self, database, create=False):
        self.db = sqlite3.Connection(database)
        self.cursor = self.db.cursor()
        if create is True:
            self.initial_creation()
        self.return_scrobble_count()
            
    def initial_creation(self):
        query = ['''
        CREATE TABLE IF NOT EXISTS `scrobble` (
        `trackid` int(8) NOT NULL,
        `scrobble_count` int(4) NOT NULL
        )''',
        
        '''CREATE TABLE IF NOT EXISTS `songs` (
        `trackid` int(8) NOT NULL,
        `artist` varchar(255) NOT NULL,
        `song` varchar(255) NOT NULL,
        `album` varchar(255) NOT NULL,
        `tracknumber` int(2) NOT NULL,
        `duration` int(6) NOT NULL,
        `usecount` int(6) NOT NULL,
        `rating` varchar(1) DEFAULT "",
        PRIMARY KEY  (`trackid`))''',
        
        '''CREATE TABLE IF NOT EXISTS `scrobble_counter` (
        `count` int(5) NOT NULL)''',
        
        '''CREATE TABLE IF NOT EXISTS `love_cache` (
        `trackid` int(8) NOT NULL,
        `love_sent` boolean DEFAULT 0,
        PRIMARY KEY (`trackid`))''',
        
        '''insert into scrobble_counter (count) values (0)''']
        
        for q in query:
            self.cursor.execute(q)
            self.db.commit()
    
    def close_connection(self):
        self.db.commit()
        self.db.close()
    
    def return_love_cache(self, internal=False):
        if internal:
            self.cursor.execute("""SELECT trackid FROM love_cache""")
            tuples = self.cursor.fetchall()
            self.love_cache = []
            for t in tuples:
                self.love_cache.append(t[0])
            return self.love_cache
        else:
            self.cursor.execute("""SELECT love_cache.trackid, songs.artist,
                                        songs.song FROM songs INNER JOIN love_cache
                                        ON songs.trackid=love_cache.trackid WHERE
                                        love_cache.love_sent=0""")
            return self.cursor.fetchall()
    
    def mark_as_love_sent(self, id_list):
        self.cursor.execute('update love_cache set love_sent=1 where trackid IN (%s)'%','.join(['?']*len(id_list)), id_list)
        self.db.commit() 
        
    
    def return_scrobble_list(self, order="RANDOM()"):
        query = """SELECT scrobble.ROWID, 
                            songs.artist, songs.song,
                            songs.duration, songs.album, songs.tracknumber,
                            songs.rating FROM songs INNER JOIN scrobble ON
                            songs.trackid=scrobble.trackid ORDER BY %s""" % order
        self.cursor.execute(query)
        return self.cursor
    
    def return_unique_scrobbles(self):
        self.cursor.execute("""SELECT DISTINCT scrobble.trackid, scrobble.scrobble_count,
                            songs.artist, songs.song,
                            songs.album, songs.rating
                            FROM songs INNER JOIN
                            scrobble ON songs.trackid=scrobble.trackid""")
        return self.cursor
    
    def return_scrobble_count(self):
        self.cursor.execute("""SELECT count from scrobble_counter""")
        self.scrobble_counter = self.cursor.fetchone()[0]
        if self.scrobble_counter > 0:
            self.had_pending_scrobbles = True
        else:
            self.had_pending_scrobbles = False
        return self.scrobble_counter
        
    def reset_scrobble_counter(self):
        """This function goes through and counts each individual
        scrobble, may be inefficent. Returns the count, resets the table counter
        and sets self.scrobble_counter"""
        self.scrobble_counter = self.cursor.execute("select COUNT(*) from scrobble").fetchone()[0]
        self.update_scrobble_count()
        return self.scrobble_counter
    
    def update_scrobble_count(self):
        self.cursor.execute("""update scrobble_counter set count=?""", (self.scrobble_counter,))
        self.db.commit()
    
    def return_tracks(self, rating):
        self.cursor.execute("""select trackid, usecount, artist, song, album, rating
                            from songs where rating=?""", (rating,))
        return self.cursor
    
    def return_pending_love(self):
        self.cursor.execute("""select songs.trackid, songs.usecount, songs.artist,
                            songs.song, songs.album, songs.rating from songs
                            inner join love_cache on songs.trackid=love_cache.trackid
                            where love_cache.love_sent=0""")
        return self.cursor

                            
                            
    def change_markings(self, id_list, marking, was_love=False):
        if marking == "D":
            _marking = u""
        else:
            _marking = marking
        #A listing of dont scrobble shouldnt affect previously loved submissions
        if marking != "D": 
            query = "update songs set rating=? where trackid IN (%s)" % ','.join(['?']*len(id_list))
            id_list.insert(0, _marking)
            data = tuple(id_list)
            self.cursor.execute(query, id_list)
            self.db.commit()
            id_list.pop(0)
        #banning or dont scrobble means deleting from scrobble list also
        if marking == "B" or marking == "D":
            self.delete_scrobbles(id_list)
        #send to love cache
        if marking == "L":
            self.add_to_love_cache(id_list)
        if was_love or marking == "B":
            self.remove_from_love_cache(id_list)
            
    def add_to_love_cache(self, id_list):
        """Takes a list of ids and checks them against the love cache, adding them if
        they dont exist"""
        try:
            self.love_cache
        except AttributeError:
            self.love_cache = self.return_love_cache(internal=True)
        for id in id_list:
            if id not in self.love_cache:
                self.cursor.execute("insert into love_cache (trackid) values (?)", (id,))
                #add new values to self.love_cache so we dont need to access db again
                self.love_cache.append(id)
        self.db.commit()
        
    def remove_from_love_cache(self, id_list):
        """Called when a user removes love from an item.
        Wont remove things that have sent love"""
        for id in id_list:
            self.cursor.execute("delete from love_cache where trackid=? and love_sent=0", (id,))
        self.db.commit()
  
 
    
    def delete_scrobbles(self, id_list):
        """Given a list of ROWIDs, will delete items from the scrobble list"""
        if id_list == 'all':
            self.cursor.execute('delete from scrobble')
            self.cursor.execute('update scrobble_counter set count=0')
            self.db.commit()
            self.scrobble_counter = 0
        else:
            self.cursor.execute('delete from scrobble where trackid IN (%s)'%','.join(['?']*len(id_list)), id_list)
            self.db.commit()
            self.reset_scrobble_counter()
    
   
    def add_new_data(self, song_dic):
        """recieves a list of a songs data, checks it against what is in
        the counter table already.  Updates the playcount if it already
        exists, or creates a new row. In both cases the scrobble table
        is added to as well."""
        self.cursor.execute("""SELECT rating, usecount FROM
                            songs WHERE trackid = ?""", (song_dic['Track ID:'],))
        row = self.cursor.fetchone()
        try:
            rating, usecount = row
        except TypeError:
            rating, usecount = song_dic['User rating:'], song_dic['Use count:']
        
        if row == None:
            num_scrobbles = song_dic['Use count:']
            self.cursor.execute("""insert into songs (trackid, artist,
                                song, album, tracknumber, duration,
                                usecount, rating) values (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (song_dic['Track ID:'], song_dic['Artist:'],
                                 song_dic['Title:'], song_dic['Album:'],
                                 song_dic['Track number:'], song_dic['Duration:'],
                                 usecount, rating))
            self.db.commit()
        else:
            
            #song has row in db
            num_scrobbles = song_dic['Use count:'] - usecount
            #If the current rating saved in the db is different from the device
            #what should we do? We currently have no way to change the rating
            #on the device so we will give priority to a 5 or 1 star on the device
            #and leave any other ratings alone
            if song_dic['User rating:'] != "":
                rating = song_dic['User rating:']
        if num_scrobbles > 0:
            self.cursor.execute("""update songs set usecount=?, rating=?
                                where trackid=?""", (song_dic['Use count:'],
                                                     rating,
                                                    song_dic['Track ID:']))
            self.db.commit()
        
        if rating == 'L':
            self.add_to_love_cache([song_dic['Track ID:']])
            
        if rating != 'B':
            self.scrobble_counter += num_scrobbles
            count = num_scrobbles
            if self.had_pending_scrobbles:
                if self.pending_scrobble_list is None:
                    self.fill_pending_scrobble_list()
                count = self.return_new_count(count, song_dic['Track ID:'])
                
            while num_scrobbles > 0:
                self.cursor.execute("""insert into scrobble (trackid, scrobble_count)
                                    values (?, ?)""", (song_dic['Track ID:'], count))
                num_scrobbles -= 1
            self.db.commit()
            
    def fill_pending_scrobble_list(self):
        #we need to check if previous scrobbles were pending
        #so we can grab the old count and update it
        #this section is not necessary unless there were some pending scrobbles
        self.cursor.execute("""select DISTINCT trackid, scrobble_count from scrobble""")
        rows = self.cursor.fetchall()
        self.pending_scrobble_list = {}
        for row in rows:
            self.pending_scrobble_list[row[0]] = row[1]

    def return_new_count(self, count, trackid):
        """Takes the scrobble count of a trackid and checks if there are pending scrobbles
        which are added"""
        try:
            old_count = self.pending_scrobble_list[trackid]
            count += old_count
            self.cursor.execute("""update scrobble set scrobble_count=? where
                                trackid=?""", (count, trackid))
            return count
        except KeyError:
            return count

        
