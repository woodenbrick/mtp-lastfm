import songDataClass
trackListing = file('./mtp-tracktest2', 'r')
sd = songDataClass.songData()
for line in trackListing.readlines():
    print 'Data: ', line
    sd.newData(line)
    
    
