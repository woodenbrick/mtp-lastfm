#!/usr/bin/env python
import songDataClass
import dbClass
import scrobbler
import os
import md5
import sys
def createDatabase():
    if not os.path.exists(path + 'lastfmDB'):
        print "Database doesn't exist, creating"
        db = dbClass.lastfmDb()
        db.initialCreation()
        db.closeConnection()

def getPath():
    """Finds the path that the script is running from"""
    path = os.path.dirname(os.path.realpath(__file__)) + '/'
    return path

def connectToMtpDevice():
    #This retrieves the tracklisting fm the MTP device, with its playcount
    print 'Connecting to MTP device...'
    os.system("mtp-tracks > "+ path + "mtp-tracklisting")
    x = file(path + 'mtp-tracklisting', 'r').readlines()
    if len(x) < 3:
        print 'Error with MTP device, try reconnecting'
        return False
    else:
        print 'Done. It is now safe to remove your MTP device.'
        return True

def addListToDb(db):
    try:
        f = file(path + 'mtp-tracklisting', 'r')
        print 'Cross checking song data with local database, may take some time...',
        songObj = songDataClass.songData()
        for line in f.readlines():
            songObj.newData(line)
            if songObj.readyForExport:
                db.addNewData(songObj)
                #run newData again, because we have a new track
                songObj.resetValues()
                songObj.newData(line)
        f.close()
        print 'Done.'
        return True
    except IOError:
        return False

def scrobbleToLastFm():
    user, password = database.returnUserDetails()
    print 'Logged in as', user
    c = database.returnScrobbleList()
    scrobble = scrobbler.Scrobbler(user, password)
    if scrobble.handshake() == 'OK':
        if scrobble.submitTracks(c):
            #delete all tracks
            database.deleteScrobbles('all')
        else:
            #delete tracks that were scrobbled
            database.deleteScrobbles(scrobble.deletionIds)
    elif handshakeResponse == 'BADAUTH':
        database.removeOldUser()
        database.createAccount()

path = getPath()
createDatabase()
database = dbClass.lastfmDb(path + 'lastfmDB')
if connectToMtpDevice():
    if addListToDb(database):
        scrobbleToLastFm()
    else:
        print 'Error retrieving new playlist, please make sure your MTP device \
    is connected'
database.closeConnection()
