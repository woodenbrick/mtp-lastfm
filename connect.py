#This module is used for all connections:
#database-> mtp file list & database->audioscrobbler

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
        """Used to check if database exists"""
        pass
    
    
    def checkAccount(self):
        result = self.db.execute('''SELECT * FROM account''')
        if result != None:
            pass
    
    def closeConnection(self):
        self.db.commit()
        self.db.close()
    
    def addNewData(self, data):
        """recieves a list of a songs data, checks it against what is in the counter table already.
        Updates the playcount if it already exists, or creates a new row. In both cases the scrobble
        table is added to as well."""
        
        
# Save (commit) the changes
db.commit()

# We can also close the cursor if we are done with it
db.close()

db = sqlite3.Connection('./lastfm')
db.cursor()
c = db.execute('select * from account')
for row in c:
    print row