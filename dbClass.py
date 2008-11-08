#This module is used for all connections:
#database-> mtp file list & database->audioscrobbler

import os
import sqlite3

class lastfmDb:
    def __init__(self, database):
        self.db = sqlite3.Connection(database)
        self.cursor = self.db.cursor()
        #self.intialCreation()
        #self.checkAccount()
        
    def initialCreation(self):
        """Used to check if database exists"""
        pass
    
    
    def checkAccount(self):
        result = self.db.execute('''SELECT * FROM account''')
        if result != None:
            pass
    
    def closeConnection(self):
        self.db.commit()
        self.db.close()
    
    def addNewData(self, songObj):
        """recieves a list of a songs data, checks it against what is in the counter table already.
        Updates the playcount if it already exists, or creates a new row. In both cases the scrobble
        table is added to as well."""
        print songObj.trackid, 'song id'
        self.cursor.execute("""SELECT id, playcount FROM songs WHERE id = ?""", (songObj.trackid,))
        row = self.cursor.fetchone()
        if row == None:
            print 'song doesnt exist'
            numScrobbles = songObj.usecount
            self.cursor.execute("""insert into songs (trackid, artist, song, album, tracknumber, duration, usecount) values
                                                   (?, ?, ?, ?, ?, ?, ?)""", (songObj.trackid, songObj.artist, songObj.song,
                                                                              songObj.album, songObj.tracknumber,
                                                                              songObj.duration, songObj.usecount))
            self.cursor.commit()
        else:
            #song has row in db
            numScrobbles = songObj.usecount - row[1]
            self.cursor.execute("""update songs set usecount=? where trackid=?""", (songObj.usecount, songObj.trackid))
            self.cursor.commit()
        if numScrobbles > 0:
            self.cursor.execute("""insert into scrobble (trackid, scrobbles) values (?, ?)""", (songObj.trackid, numScrobbles))
            self.cursor.commit()
