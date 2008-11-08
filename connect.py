#This module is used for all connections:
#database-> mtp file list & database->audioscrobbler

import os
import sqlite3

#This retrieves the tracklisting fm the MTP device, with its playcount
#listing = os.system("mtp-tracks >/home/wode/mtp-tracklisting")

class lastfmDb:
    def __init__(self):
        self.db = sqlite3.Connection('./lastfm')
        self.cursor = self.db.cursor()
        #self.intialCreation()
        self.checkAccount()
        
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
        self.cursor.execute("""SELECT trackid, playcount FROM songs WHERE trackid = 
        
        
         if i == None:
            print 'song doesnt exist'
            numScrobbles = data[6]
            c.execute("""insert into songs (id, artist, song, 
                                                   album, tracknumber, duration, playcount) values
                                                   (?, ?, ?, ?, ?, ?, ?)""", (data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
            conn.commit()
        else:
            numScrobbles = data[6] - i[1]
            c.execute("""update songs set playcount=? where id=?""", (data[6], data[0]))
        if numScrobbles > 0:
            c.execute("""insert into scrobble (trackid, scrobbles) values (?, ?)""", (data[0], numScrobbles))
            conn.commit()
        
# Save (commit) the changes
db.commit()

# We can also close the cursor if we are done with it
db.close()

db = sqlite3.Connection('./lastfm')
db.cursor()
c = db.execute('select * from account')
for row in c:
    print row