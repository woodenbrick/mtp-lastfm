from songDataClass import songData

trackListing = file('./mtp-tracklisting', 'r')
for line in trackListing.readlines():
    if line.__contains__('Track ID'):
        
    
