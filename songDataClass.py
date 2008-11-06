import string
import re

class songData:
    def __init__(self):
        self.songData = []
        self.max = 7 #count of all possible song data
        self.requiredData = ['Track ID', 'Title', 'Artist', 'Album', 'Track number', 
                             'Duration', 'Use Count']
        
    def _isData(self, data):
        """Returns true if the data submitted is data we want"""
        for item in self.requiredData:
            if data.__contains__(item):
                return True
            if data.__contains__('Filetype'):
                self.checkFiletype(data)
        return False
        
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
        if self._isData(newData):
            clean = self._cleanData(newData)
            self.songData.append(clean)
    
    def checkFiletype(self, filetype):
        """if this is called we are at the end of the song.
        check that its a valid type mp3, check if use count exists and if not append"""
        if self.checkIfFull():
            
        
        
    def checkIfFull(self):
        """Returns true if all songdata is available. Note that Use Count wont exist
        if the song has never been played"""
        if len(self.songData) == self.max:
            return True
        else:
            return False
        
    def checkSongDataCount(self):
        return len(self.songData)
    