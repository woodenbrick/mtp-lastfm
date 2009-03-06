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
import md5
import getpass
from logger import Logger

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
        `time` integer(20) NOT NULL,
        `sessionkey` varchar(255) DEFAULT ""
        )''',
        '''CREATE TABLE IF NOT EXISTS `devices` (
        `username` varchar(100) NOT NULL,
        `serial_number` varchar(255) NOT NULL,
        `friendly_name` varchar(100) NOT NULL
        )''',
        '''CREATE TABLE IF NOT EXISTS `options` (
        `username` varchar(100) NOT NULL,
        `scrobble_order_random` boolean DEFAULT 1,
        `scrobble_order_alpha` boolean DEFAULT 0,
        `connect_on_startup` boolean DEFAULT 0,
        `auto_scrobble` boolean DEFAULT 0,
        `scrobble_time` integer(3) DEFAULT 8.5,
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
        print query
        self.cursor.execute(query)
        self.db.commit()

    def remove_user(self, username):
        self.cursor.execute("delete from users where username=?", (username,))
        self.cursor.execute("delete from options where username=?", (username,))
        self.db.commit()
        
    def update_options(self, username, *args):
        print 'updating', username, args
        query = """update options set scrobble_order_random=%d, scrobble_order_alpha=%d,
        connect_on_startup=%d, auto_scrobble=%d, scrobble_time=%d,
        use_default_time=%d WHERE username='%s'""" % (args[0], args[1], args[2], args[3], args[4], args[5], username)
        self.cursor.execute(query)
        self.db.commit()
    
    def retrieve_options(self, username):
        self.cursor.execute("""select scrobble_order_random,
                            scrobble_order_alpha, connect_on_startup, 
                        auto_scrobble, scrobble_time, use_default_time from
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
        self.log = Logger(name='sqliteDb Log')
        if create is True:
            self.initialCreation()
        self.returnScrobbleCount()
            
    def initialCreation(self):
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
        `rating` varchar(1),
        PRIMARY KEY  (`trackid`))''',
        
        '''CREATE TABLE IF NOT EXISTS `scrobble_counter` (
        `count` int(5) NOT NULL)''',
        
        '''insert into scrobble_counter (count) values (0)''']
        
        print 'Creating Tables'
        for q in query:
            self.cursor.execute(q)
            self.db.commit()
    
    def closeConnection(self):
        self.db.commit()
        self.db.close()
    
    def returnScrobbleList(self, order):
        self.cursor.execute("""SELECT scrobble.ROWID, 
                            songs.artist, songs.song,
                            songs.duration, songs.album, songs.tracknumber,
                            songs.rating FROM songs INNER JOIN scrobble ON
                            songs.trackid=scrobble.trackid ORDER BY ?""", (order,))
        return self.cursor
    
    def returnUniqueScrobbles(self):
        self.cursor.execute("""SELECT DISTINCT scrobble.trackid, scrobble.scrobble_count,
                            songs.artist, songs.song,
                            songs.album, songs.rating
                            FROM songs INNER JOIN
                            scrobble ON songs.trackid=scrobble.trackid""")
        return self.cursor
    
    def returnScrobbleCount(self):
        self.cursor.execute("""SELECT count from scrobble_counter""")
        self.scrobble_counter = self.cursor.fetchone()[0]
        return self.scrobble_counter
        
    def resetScrobbleCounter(self):
        """This function goes through and counts each individual
        scrobble, may be inefficent. Returns the count, resets the table counter
        and sets self.scrobble_counter"""
        self.cursor.execute("select scrobble_count from scrobble")
        rows = self.cursor.fetchall()
        total = 0
        for r in rows:
            total += 1
        self.scrobble_counter = total
        self.updateScrobbleCount()
        return self.scrobble_counter
    
    def updateScrobbleCount(self):
        self.cursor.execute("""update scrobble_counter set count=?""", (self.scrobble_counter,))
        self.db.commit()
    
    def execute(self, query):
        """wrapper for executing arbitrary queries"""
        self.cursor.execute(query)
        return self.cursor
    
    def mark_songs_as_loved(self, idList):
        #depreciated
        """Takes a list of ids and marks them as loved"""
        self.cursor.execute("update songs set rating='L' where trackid IN (%s)"%','.join(['?']*len(idList)), idList)
        self.db.commit()
        
    def mark_songs_as_banned_or_no_scrobble(self, idList, marking=None):
        #depreciated
        new_scrobble_count = self.scrobble_counter - len(idList)
        self.cursor.execute("""delete from scrobble where trackid IN (%s)"""%','.join(['?']*len(idList)), idList)
        if marking is "B":
            self.cursor.execute("""update songs set rating='B' where trackid IN (%s)"""%','.join(['?']*len(idList)), idList)
            self.cursor.execute("""update scrobble_counter set count=?""", (new_scrobble_count,))
        self.scrobble_counter = self.returnScrobbleCount()
        self.db.commit()
    
    def return_tracks(self, rating):
        self.cursor.execute("""select trackid, usecount, artist, song, album, rating
                            from songs where rating=?""", (rating,))
        return self.cursor
    
    def change_markings(self, idList, marking):
        if marking == "D":
            _marking = "''"
        else:
            _marking = "%s" % marking
        query = "update songs set rating=? where trackid IN (%s)" % ','.join(['?']*len(idList))
        idList.insert(0, _marking)
        data = tuple(idList)
        self.cursor.execute(query, idList)
        self.db.commit()
        #banning or dont scrobble means deleting from scrobble list also
        if marking == "B" or marking == "D":
            idList.pop(0)
            self.deleteScrobbles(idList)
            
    
    def deleteScrobbles(self, idList):
        """Given a list of ROWIDs, will delete items from the scrobble list"""
        self.log.logger.info('The following ids will be deleted from the scrobble list: ' + ''.join(str(idList)))
        if idList == 'all':
            self.cursor.execute('delete from scrobble')
            self.cursor.execute('update scrobble_counter set count=0')
            self.db.commit()
            self.scrobble_counter = 0
        else:
            self.cursor.execute('delete from scrobble where trackid IN (%s)'%','.join(['?']*len(idList)), idList)
            self.db.commit()
            self.resetScrobbleCounter()
    
    def commit(self):
        """commit wrapper"""
        self.db.commit()
    
   
    def addNewData(self, songObj):
        """recieves a list of a songs data, checks it against what is in
        the counter table already.  Updates the playcount if it already
        exists, or creates a new row. In both cases the scrobble table
        is added to as well."""
        self.cursor.execute("""SELECT trackid, usecount FROM songs WHERE trackid = ?""", (songObj.trackid,))
        row = self.cursor.fetchone()
        if row == None:
            numScrobbles = songObj.usecount
            self.cursor.execute("""insert into songs (trackid, artist,
                                song, album, tracknumber, duration,
                                usecount, rating) values (?, ?, ?, ?, ?, ?, ?, '')""",
                                (songObj.trackid, songObj.artist, songObj.title,
                                 songObj.album, songObj.tracknumber,
                                 songObj.duration, songObj.usecount))
            self.db.commit()
        else:
            #song has row in db
            numScrobbles = songObj.usecount - row[1]
        if numScrobbles > 0:
            self.cursor.execute("""update songs set usecount=?
                                where trackid=?""", (songObj.usecount,
                                                    songObj.trackid))
            self.db.commit()
        self.scrobble_counter += numScrobbles
        count = numScrobbles
        while numScrobbles > 0:
            self.cursor.execute("""insert into scrobble (trackid, scrobble_count)
                                values (?, ?)""", (songObj.trackid, count))
            numScrobbles -= 1
        self.db.commit()
