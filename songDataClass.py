import string
import re

class songData:
    def __init__(self):
        self.songData = []
        self.max = 7 #count of all possible song data
        self.requiredData = ['Title', 'Artist', 'Album', 'Track number', 
                             'Duration', 'Use Count']
        
    def _isData(self, data):
        """Returns true if the data submitted is data we want"""
        for item in self.requiredData:
            if data.__contains__(item):
                return True
            if data.__contains__('Track ID'):
                print 'TRACK ID'
                self.checkFiletype(data)
        return False
        
    def _cleanData(self, data):
        """Strips unneeded info"""
        cleanedData = string.split(data, ': ')[1:-1]
        return cleanedData
    
    def _getKey(self, data):
        """returns the key (eg. Album) for a string"""
        key = string.split(data, ':')[0][:-1]
        return key
        
    def newData(self, newData):
        """Needs to find out what data it is and assign 
        it to the correct variable"""
        if self._isData(newData):
            clean = self._cleanData(newData)
            self.songData.append(clean)
        else:
            pass
            
    def checkFiletype(self, filetype):
        """if this is called we are at the end of the song. OR at the very first song
        check that its a valid type mp3, check if use count exists and if not append"""
        print 'calling checkFiletype'
        if self.checkIfFull():
            #use count exists
            print 'all accounted for'
            print self.songData
        elif self.checkSongDataCount() == 6:
            self.songData.append(0)
            print 'use count missing'
            print self.songData
        if self.checkSongDataCount() == 0:
            print 'data is 0'
            #Add track ID to the songData array
            clean = self._cleanData(filetype)
            self.songData.append(clean)
        #resetdata for next song
        else:
            self.resetValues()
        
        
    def checkIfFull(self):
        """Returns true if all songdata is available. Note that Use Count wont exist
        if the song has never been played"""
        if len(self.songData) == self.max:
            return True
        else:
            return False
        
    def checkSongDataCount(self):
        return len(self.songData)
    
    def resetValues(self):
        self.songData = []
        
        
def run():
    trackListing = file('./mtp-tracktest2', 'r')
    sd = songData()
    for line in trackListing.readlines():
        print 'Data: ', line
        sd.newData(line)

if __name__ == "__main__":
    run()