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

songObj = songDataClass.songData()
database = dbClass.lastfmDb('./lastfmDB')
f = file('./mtp-tracklisting', 'r')


def connectToMtpDevice():
    #This retrieves the tracklisting fm the MTP device, with its playcount
    print 'Connecting to MTP device...'
    os.system("mtp-tracks >./mtp-tracklisting")
    
    x = f.readlines()
    if len(x) < 3:
        print x
        return False
    else:
        print 'Done. It is now safe to remove your MTP device.'
        f.seek(0)
        return True


def addListToDb():
    print 'Cross checking song data with local database, may take some time...',
    for line in f.readlines():
        songObj.newData(line)
        if songObj.readyForExport:
            database.addNewData(songObj)
            #run newData again, because we have a new track
            songObj.resetValues()
            songObj.newData(line)
    print 'Done.'

def scrobbleToLastFm():
    deleteList = []
    user, password = database.returnUserDetails()
    print 'Logged in as', user
    c = database.returnScrobbleList()
    scrobble = scrobbler.Scrobbler(user, password)
    if scrobble.handshake():
        scrobble.submitTracks(c)
    database.deleteScrobbles(scrobble.deletionIds)


connectToMtpDevice()
addListToDb()
scrobbleToLastFm()
database.closeConnection()