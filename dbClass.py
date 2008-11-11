#This module is used for all connections:
#database-> mtp file list & database->audioscrobbler

import os
import sqlite3
import md5
import getpass

class lastfmDb:
    def __init__(self, database='./lastfmDB'):
        self.db = sqlite3.Connection(database)
        self.cursor = self.db.cursor()
        #self.intialCreation()
        #self.checkAccount()
        
    def initialCreation(self):
        query = ['''
        CREATE TABLE IF NOT EXISTS `scrobble` (`trackid` int(8) NOT NULL)''',
        
        '''CREATE TABLE IF NOT EXISTS `songs` (
        `trackid` int(8) NOT NULL,
        `artist` varchar(255) NOT NULL,
        `song` varchar(255) NOT NULL,
        `album` varchar(255) NOT NULL,
        `tracknumber` int(2) NOT NULL,
        `duration` int(6) NOT NULL,
        `usecount` int(6) NOT NULL,
        PRIMARY KEY  (`trackid`))''',
        
        '''CREATE TABLE IF NOT EXISTS `users` (
        `username` varchar(100) NOT NULL,
        `password` varchar(255) NOT NULL
        )''']
        print 'Creating Tables'
        for q in query:
            self.cursor.execute(q)
            self.db.commit()
    
    
    def createAccount(self):
        username = raw_input("last.fm username: ")
        password = getpass.default_getpass()
        password = md5.new(password).hexdigest()
        self.cursor.execute("INSERT INTO users (username, password) values ('?', '?')", (user, password))
        'BREAKS HERE!!!!'
        #self.db.commit()
        self.cursor.execute("SELECT * FROM users")
        row = self.cursor.fetchone()
        return row
            
    def closeConnection(self):
        self.db.commit()
        self.db.close()
    
    def returnScrobbleList(self):
        self.cursor.execute('SELECT scrobble.ROWID, songs.artist, songs.song, songs.duration, songs.album, songs.tracknumber FROM songs INNER JOIN scrobble ON songs.trackid=scrobble.trackid')
        return self.cursor
    
    def execute(self, query):
        """wrapper for executing arbitrary queries"""
        self.cursor.execute(query)
        return self.cursor
    
    def deleteScrobbles(self, idList):
        """Given a list of ROWIDs, will delete items from the scrobble list"""
        for id in idList:
            self.cursor.execute('delete from scrobble where id=?', (id,))
            self.db.commit()
    
    def commit(self):
        """commit wrapper"""
        self.db.commit()
    
    def returnUserDetails(self):
        self.cursor.execute("""SELECT username, password FROM users""")
        print 'running'
        row = self.cursor.fetchone()
        if row == None:
            row = self.createAccount()
        return row[0], row[1]
    
    def addNewData(self, songObj):
        """recieves a list of a songs data, checks it against what is in the counter table already.
        Updates the playcount if it already exists, or creates a new row. In both cases the scrobble
        table is added to as well."""
        self.cursor.execute("""SELECT trackid, usecount FROM songs WHERE trackid = ?""", (songObj.trackid,))
        row = self.cursor.fetchone()
        if row == None:
            numScrobbles = songObj.usecount
            self.cursor.execute("""insert into songs (trackid, artist, song, album, tracknumber, duration, usecount) values
                                                   (?, ?, ?, ?, ?, ?, ?)""", (songObj.trackid, songObj.artist, songObj.title,
                                                                              songObj.album, songObj.tracknumber,
                                                                              songObj.duration, songObj.usecount))
            self.db.commit()
        else:
            #song has row in db
            numScrobbles = songObj.usecount - row[1]
            self.cursor.execute("""update songs set usecount=? where trackid=?""", (songObj.usecount, songObj.trackid))
            self.db.commit()
        while numScrobbles > 0:
            print songObj.trackid
            self.cursor.execute("""insert into scrobble (trackid) values (?)""", (songObj.trackid,))
            numScrobbles -= 1
            self.db.commit()
