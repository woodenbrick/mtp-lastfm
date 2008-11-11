#!/usr/bin/env python
import songDataClass
import dbClass
import scrobbler


#This retrieves the tracklisting fm the MTP device, with its playcount
#listing = os.system("mtp-tracks >/home/wode/mtp-tracklisting")

f = file('./mtp-tracktest2', 'r')
songObj = songDataClass.songData()
database = dbClass.lastfmDb('./lastfm')

#into db
print 'Cross checking song data with local database'
for line in f.readlines():
    songObj.newData(line)
    if songObj.readyForExport:
        database.addNewData(songObj)
        #run newData again, because we have a new track
        songObj.resetValues()
        songObj.newData(line)


#out to lastfm
deleteList = []
user, password = database.returnUserDetails()
print 'Logged in as', user
c = database.returnScrobbleList()
scrobble = scrobbler.Scrobbler(user, password)
if scrobble.handshake():
    if scrobble.submitTracks(c):
        deleteList.extend(scrobble.deletionIds)
print deleteList
database.closeConnection()