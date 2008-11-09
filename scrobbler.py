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
            self.sessionID = conn.readline().strip
            self.nowPlayingUrl = conn.readline().strip #not used at this time
            self.submissionUrl = conn.readline().strip
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
        db = dbClass.lastfmDb()
        tracks = db.returnScrobbleList()
        trackList = []
        for t in tracks:
            trackList.append(t)
        print trackList
        
        #self.submissionUrl
        #postValues = {"s" : self.sessionID,
        #              "a[0]" : self.
        #self.url += r"/?" +self.encodeUrl()
        #conn = urllib2.urlopen(self.url)




#m[0]=<mb-trackid>
#    The MusicBrainz Track ID, or an empty string if not known.
#
#Key-value pairs are separated by an '&' character, in the usual manner for form
#submissions in HTTP. The values must be converted to UTF-8 first, and must be
#URL encoded. Multiple submissions may be specified by repeating the a[], t[],
#i[], o[], r[], l[], b[], n[], and m[] key-value pairs with increasing indices.
#(e.g. a[1], a[2] etc.) Note that when performing multiple submissions, the
#tracks must be submitted in chronological order according to when they were
#listened to (i.e. the track identified by t[0].. must have been played before
#the track identified by t[1].. and so on). 3.3 Submission Response
#
#The body of the server response will consist of a single \n (ASCII 10)
#terminated line. The client should process the first line of the body to
#determine the action it should take:
#
#OK
#    This indicates that the submission request was accepted for processing. It
#    does not mean that the submission was valid, but only that the
#    authentication and the form of the submission was validated. The client
#    should remove the submitted track(s) from its queue.
#BADSESSION
#    This indicates that the Session ID sent was somehow invalid, possibly
#    because another client has performed a handshake for this user. On receiving
#    this, the client should re-handshake with the server before continuing. The
#    client should not remove submitted tracks from its queue.
#FAILED <reason>
#    This indicates that a failure has occurred somewhere. The reason indicates
#    the cause of the failure. Clients should treat this as a hard failure, and
#    should proceed as directed in the failure handling section. The client
#    should not remove submitted tracks from its queue.
#        
   
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


