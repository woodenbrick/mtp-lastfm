#!/usr/bin/env python
import songDataClass
import dbClass
import scrobbler
import os
import md5
import shutil

def createDatabase():
    if not os.path.exists('./lastfmDB'):
        print "Database doesn't exist, creating"
        db = dbClass.lastfmDb()
        db.initialCreation()
        db.closeConnection()



def connectToMtpDevice():
    #This retrieves the tracklisting fm the MTP device, with its playcount
    print 'Connecting to MTP device...'
    os.system("mtp-tracks >./mtp-tracklisting")
    x = file('./mtp-tracklisting', 'r').readlines()
    if len(x) < 3:
        print x
        return False
    else:
        print 'Done. It is now safe to remove your MTP device.'
        return True

def addListToDb():
    try:
        f = file('./mtp-tracklisting', 'r')
        print 'Cross checking song data with local database, may take some time...',
        for line in f.readlines():
            songObj.newData(line)
            if songObj.readyForExport:
                database.addNewData(songObj)
                #run newData again, because we have a new track
                songObj.resetValues()
                songObj.newData(line)
        f.close()
        shutil.move('./mtp-tracklisting', 'mtp-tracklisting.OLD')
        print 'Done.'
        return True
    except IOError:
        return False

def scrobbleToLastFm():
    user, password = database.returnUserDetails()
    print 'Logged in as', user
    c = database.returnScrobbleList()
    scrobble = scrobbler.Scrobbler(user, password)
    if scrobble.handshake():
        if scrobble.submitTracks(c):
            #delete all tracks
            database.deleteScrobbles('all')
        else:
            #delete tracks that were scrobbled
            database.deleteScrobbles(scrobble.deletionIds)

createDatabase()
database = dbClass.lastfmDb('./lastfmDB')
songObj = songDataClass.songData()
connectToMtpDevice()
if addListToDb():
    scrobbleToLastFm()
else:
    print 'Error retrieving new playlist, please make sure your MTP device \
is connected'
database.closeConnection()
