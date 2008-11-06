import string
import re

class songData:
    def __init__(self):
        self.songData = []
        self.max = 7 #count of all possible song data
        
    def _cleanData(self, data):
        """Strips unneeded info"""
        cleanedData = string.split(data, ': ')[1]
        return cleanedData
    
    def _getKey(self, data):
        """returns the key (eg. Album) for a string"""
        key = string.split(data, ':')[0][:-1]
        return key
        
    def newData(self, newData):
        """Needs to find out what data it is and assign 
        it to the correct variable"""
        clean = self._cleanData(newData)
        self.songData.append(clean)
    
    def checkIfFull(self):
        """Returns true if all songdata is available"""
        if len(self.songData) == self.max:
            return True
        else:
            return False
        
    def checkSongDataCount(self):
        return len(self.songData)
    