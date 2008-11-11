#!/usr/bin/env python
import songDataClass
import dbClass
import scrobbler


#This retrieves the tracklisting fm the MTP device, with its playcount
print 'Connecting to MTP device...'
listing = os.system("mtp-tracks >./mtp-tracklisting")
print 'Done. It is now safe to remove your MTP device.'

f = file('./mtp-tracklisting', 'r')
songObj = songDataClass.songData()
database = dbClass.lastfmDb('./lastfm')

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