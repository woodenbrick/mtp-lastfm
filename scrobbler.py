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
        if self.handshake():
            #run scrobbles
            self.submitTracks()
        else:
            #end program
            pass
    
    
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
        
    def submitTracks(self):
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
        db = dbClass.lastfmDb()
        c = db.returnScrobbleList()
        
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

                a = []
                t = []
                i = []
                o = []
                r = []
                l = []
                b = []
                n = []
                m = []
                fullList = [a, t, l, b, n, i, o, r, m]
                pastTime = time.time() - 3600 #this is an hour in the past where we will start our scrobbling
                for track in cache:
                    for index in range(0, len(fullList)):
                        if index < 5:
                            fullList[index].append(track[index])
                        elif index == 5:
                            #append time, use l to work out
                            #this needs to be corrected
                            length = fullList[2][0]
                            pastTime += length
                            fullList[index].append(pastTime)
                        elif index == 6:
                            #source (always P)
                            fullList[index].append("P")
                        elif index > 6:
                            #empty strings for music brain tags and rating
                            fullList[index].append("")
                            
                a = fullList[0]
                t = fullList[1]
                i = fullList[2]
                o = fullList[3]
                r = fullList[4]
                l = fullList[5]
                b = fullList[6]
                n = fullList[7]
                m = fullList[8]
                postValues = { "s" : self.authenticationCode }
                for ind in range(0, len(a)):
                    #needs refactorindng
                    vala = "a[%d]" % ind
                    postValues[vala] = a[ind]
                    valt = "t[%d]" % ind
                    postValues[valt] = t[ind]
                    vali = "i[%d]" % ind
                    postValues[vali] = i[ind]
                    valo = "o[%d]" % ind
                    postValues[valo] = o[ind]
                    valr = "r[%d]" % ind
                    postValues[valr] = r[ind]
                    vall = "l[%d]" % ind
                    postValues[vall] = l[ind]
                    valb = "b[%d]" % ind
                    postValues[valb] = b[ind]
                    valn = "n[%d]" % ind
                    postValues[valn] = n[ind]
                    valm = "m[%d]" % ind
                    postValues[valm] = m[ind]
                postValues = urllib.urlencode(postValues)
                print postValues
                self.submitSongs(postValues)
        
    def submitSongs(self, postValues):
        req = urllib2.Request(url=self.submissionUrl, data=postValues)
        url_handle = urllib2.urlopen(req)
        response = url_handle.readline().strip()
        if response == 'OK':
            #remove tracks from cache
            print 'success'
        elif response == 'BADSESSION':
            pass
            #handshake again dont delete cache
        elif response.startswith('FAILED'):
            print 'Scrobbling Failure:', response
   
    def encodeUrl(self):
        u = urllib.urlencode({
            "hs":"true",
            "p":"1.2.1",
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


