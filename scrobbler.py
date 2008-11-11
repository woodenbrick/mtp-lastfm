import md5
import time
import urllib
import urllib2
import string
import dbClass


class Scrobbler:
    
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.client = 'tst'
        self.version = '1.0'
        self.url = "http://post.audioscrobbler.com:80"
        self.deletionIds = []
    
    
    def handshake(self):
        self.timestamp = self.createTimestamp()
        self.authenticationCode = self.createAuthenticationCode()
        self.url += r"/?" +self.encodeUrl()
        conn = urllib2.urlopen(self.url)
        self.serverResponse = conn.readline().strip()
        if self.serverResponse == 'OK':
            print 'Server response OK.'
            self.sessionID = conn.readline()[:-1]
            self.nowPlayingUrl = conn.readline().strip #not used at this time
            self.submissionUrl = conn.readline()[:-1]
            return True
        elif self.serverResponse == 'BADAUTH':
            print 'user details incorrect'
        elif self.serverResponse == 'BANNED':
            print 'this scrobbling client has been banned from submission, please notify the developer'
        elif self.serverResponse == 'BADTIME':
            print 'timestamp is incorrect, please check your clock settings'
        elif self.serverResponse.startswith('FAILED'):
            print 'Connection to server failed:', string.split(response, ' ')[1:]
        return False
        
    def submitTracks(self, c):
        """Takes c, a cursor object with scrobble data and tries to submit it to last.fm"""
        while True:
            cache = c.fetchmany(10)
            if len(cache) == 0:
                break
            else:
            #s=<sessionID>  The Session ID string returned by the handshake request. Required.
            #a[0]=<artist>  The artist name. Required.
            #t[0]=<track>   The track title. Required.
            #i[0]=<time>    The time the track started playing, in UNIX timestamp format
            #o[0]=<source>  Put P for this value
            #r[0]=<rating>  Blank or dont use
            #l[0]=<secs>    The length of the track in seconds. 
            #b[0]=<album>   The album title, or an empty string if not known.
            #n[0]=<tracknumber>The position of the track on the album, or an empty string if not known.
            #m[0]=music brainz identifier, leave blank
                fullList = [[], [], [], [], [], []]
                pastTime = int(time.time() - 3600) #this is an hour in the past where we will start our scrobbling
                size = len(cache)
                for track in cache:
                    for index in range(0, len(fullList)):
                        fullList[index].append(track[index])
                #remove row ID's which will be used for deletions
                self._delIds = fullList.pop(0)
                #append extra lists to fullList
                while len(fullList) < 9:
                    fullList.append([])
                for extra in range(0, len(cache)):
                    #append time, use l to work out
                    length = fullList[2][extra]
                    pastTime += length
                    fullList[5].append(pastTime)
                    #append source (always P)
                    fullList[6].append(u"P")
                    #empty strings for music brain tags and rating
                    fullList[7].append(u"")
                    fullList[8].append(u"")
                    
                postValues = { "s" : self.sessionID }
                for i in range(0, size):
                    dic = self.getDicValue(i)
                    for j in range (0, len(dic)): #haha!
                        postValues[dic[j]] = fullList[j][i]
                postValues = urllib.urlencode(postValues)
                if not self._sendPost(postValues):
                    print 'Error posting to last.fm'
                    return False
                else:
                    continue
                    
                
    def getDicValue(self, i):
        """Returns a list of dictionary keys for a specified index"""
        values = "atlbniorm"
        list = []
        for v in values:
            list.append("%s[%d]" % (v, i))
        return list
        
    def _sendPost(self, postValues):
        req = urllib2.Request(url=self.submissionUrl, data=postValues)
        url_handle = urllib2.urlopen(req)
        response = url_handle.readline().strip()
        if response == 'OK':
            #remove tracks from cache
            print 'Success'
            self.deletionIds.extend(self._delIds)
            return True
        elif response == 'BADSESSION':
            print 'Bad session'
            pass
            #handshake again dont delete cache
            return False
        elif response.startswith('FAILED'):
            print 'Scrobbling Failure:', response
            return False
   
    def encodeUrl(self):
        u = urllib.urlencode({
            "hs":"true",
            "p":"1.2",
            "c":self.client,
            "v":self.version,
            "u":self.user,
            "t":self.timestamp,
            "a":self.authenticationCode})
        return u
    
    def createAuthenticationCode(self):
        code = md5.new(self.password + self.timestamp).hexdigest()
        return code
    
    def createTimestamp(self):
        stamp = str(int(time.time()))
        return stamp
    

def run():
    password = md5.new('mst1PatyF').hexdigest()
    scrobbler = Scrobbler('woodenbrick', password)
    
if __name__ == '__main__':
    run()


