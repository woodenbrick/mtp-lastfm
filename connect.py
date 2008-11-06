import os
import sqlite3

#This retrieves the tracklisting fm the MTP device, with its playcount
#listing = os.system("mtp-tracks >/home/wode/mtp-tracklisting")

class lastfmDb:
    def __init__(self):
        self.db = sqlite3.Connection('./lastfm')
        self.db.cursor()
        #self.intialCreation()
        self.checkAccount()
        
    def initialCreation(self):
        self.db.execute('''create table IF NOT EXISTS songs
(trackid integer, artist text, song text, album text,
 playcount integer)''')
        #todo: fix to md5
        self.db.execute('''create table IF NOT EXISTS account 
(username text, password text)''')
    
    def checkAccount(self):
        result = self.db.execute('''SELECT * FROM account''')
        if result != None:
            pass
    
    def closeConnection(self):
        self.db.commit()
        self.db.close()
        
# Save (commit) the changes
db.commit()

# We can also close the cursor if we are done with it
db.close()

db = sqlite3.Connection('./lastfm')
db.cursor()
c = db.execute('select * from account')
for row in c:
    print row