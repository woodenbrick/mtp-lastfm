#This module is used for all connections:
#database-> mtp file list & database->audioscrobbler

import os
import sqlite3
import md5
import getpass
from logger import Logger

class lastfmDb_Users:
    def __init__(self):
        if not os.path.exists("usersDB"):
            self.create_new_database()    
        self.db = sqlite3.Connection("usersDB")
        self.cursor = self.db.cursor()
        
    
    def create_new_database(self):
        connection = sqlite3.Connection("usersDB")
        query = '''CREATE TABLE IF NOT EXISTS `users` (
        `username` varchar(100) NOT NULL,
        `password` varchar(255) NOT NULL,
        `remember_me` boolean NOT NULL,
        `current` boolean NOT NULL
        )'''
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        
    def get_current_user(self):
        """Returns the user who last logged in and chose to remember their password"""
        self.cursor.execute("SELECT * FROM users WHERE remember_me = 'True' ORDER BY current")
        current_user = self.cursor.fetchone()
        return current_user 

#cli
class lastfmDb:
    def __init__(self, database):
        self.db = sqlite3.Connection(database)
        self.cursor = self.db.cursor()
        self.log = Logger(name='sqliteDb Log')
        
    def initialCreation(self):
        query = ['''
        CREATE TABLE IF NOT EXISTS `scrobble` (
        `trackid` int(8) NOT NULL
        )''',
        
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
        self.log.logger.info('Creating Tables')
        for q in query:
            self.cursor.execute(q)
            self.db.commit()
    
    def removeOldUser(self):
        self.cursor.execute('delete from users')
        self.db.commit()
        self.log.logging.info('Deleting old user')
    
    def createAccount(self):
        username = raw_input("last.fm username: ")
        password = getpass.default_getpass()
        password = md5.new(password).hexdigest()
        self.cursor.execute("INSERT INTO users (username, password) values (?, ?)", (username, password))
        self.db.commit()
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
        self.log.logger.info('The following ids will be deleted from the scrobble list: ' + ''.join(str(idList)))
        if idList == 'all':
            self.cursor.execute('delete from scrobble')
            self.db.commit()
        else:
            for id in idList:
                self.cursor.execute('delete from scrobble where trackid=?', (id,))
                self.db.commit()
    
    def commit(self):
        """commit wrapper"""
        self.db.commit()
    
    def returnUserDetails(self):
        self.cursor.execute("""SELECT username, password FROM users""")
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
            if numScrobbles > 0:
                self.cursor.execute("""update songs set usecount=? where trackid=?""", (songObj.usecount, songObj.trackid))
                self.db.commit()
        while numScrobbles > 0:
            self.cursor.execute("""insert into scrobble (trackid) values (?)""", (songObj.trackid,))
            numScrobbles -= 1
            self.db.commit()
