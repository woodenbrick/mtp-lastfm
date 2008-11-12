#!/usr/bin/env python
import songDataClass
import dbClass
import scrobbler
import os

#inital db creation

if not os.path.exists('./lastfmDB'):
    print "Database doesn't exist, creating"
    db = dbClass.lastfmDb()
    db.initialCreation()

#This retrieves the tracklisting fm the MTP device, with its playcount
print 'Connecting to MTP device...'
os.system("mtp-tracks >./mtp-tracklisting")

songObj = songDataClass.songData()
database = dbClass.lastfmDb('./lastfmDB')
f = file('./mtp-tracklisting', 'r')

if f.readline().__contains__('No Devices have been found'):
    print 'No devices where found'
else:
    print 'Done. It is now safe to remove your MTP device.'



#into db
print 'Cross checking song data with local database, may take some time...',
for line in f.readlines():
    songObj.newData(line)
    if songObj.readyForExport:
        database.addNewData(songObj)
        #run newData again, because we have a new track
        songObj.resetValues()
        songObj.newData(line)
print 'Done.'

#out to lastfm
deleteList = []
user, password = database.returnUserDetails()
print 'Logged in as', user
c = database.returnScrobbleList()
scrobble = scrobbler.Scrobbler(user, password)
if scrobble.handshake():
    scrobble.submitTracks(c)
database.deleteScrobbles(scrobble.deletionIds)
database.closeConnection()