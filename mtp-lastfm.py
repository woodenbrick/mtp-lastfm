#!/usr/bin/env python
import songDataClass
import dbClass


#This retrieves the tracklisting fm the MTP device, with its playcount
#listing = os.system("mtp-tracks >/home/wode/mtp-tracklisting")

f = file('./mtp-tracklisting', 'r')
songObj = songDataClass.songData()
database = dbClass.lastfmDb('./lastfm')
for line in f.readlines():
    songObj.newData(line)
    if songObj.readyForExport:
        database.addNewData(songObj)
        #run newData again, because we have a new track
        songObj.resetValues()
        songObj.newData(line)

database.closeConnection()