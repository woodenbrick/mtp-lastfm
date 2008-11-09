import sqlite3
import httplib
import md5
import time
import urllib
import urllib2

#c = sqlite3.Connection('./lastfm')
#cursor = c.cursor()
#cursor.execute('SELECT songs.*, scrobble.scrobbles FROM songs INNER JOIN scrobble ON songs.trackid=scrobble.trackid')
#for i in cursor:
#    print i



#The common parameters and their values are explained below (strings between angle brackets should be replaced by "real" values):
#hs=true
#    Indicates that a handshake is requested. Requests without this parameter set to true will return a human-readable informational message and no handshake will be performed.
#p=1.2.1
#    Is the version of the submissions protocol to which the client conforms.
#c=<client-id>
#    Is an identifier for the client (See section 1.1).
#v=<client-ver>
#    Is the version of the client being used.
#u=<user>
#    Is the name of the user.
#t=<timestamp>
#    Is a UNIX Timestamp representing the current time at which the request is being performed.
#a=<authentication-token>
#    Is the authentication token (See section 1.2 and section 1.3).
#api_key=<api_key>
#    The API key from your Web Services account. Required for Web Services authentication only.
#sk=<session_key>
#    The Web Services session key generated via the authentication protocol. Required for Web Services authentication only.

class Scrobbler:
    
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.client = 'tst'
        self.version = '1.0'
        self.url = "http://post.audioscrobbler.com:80"
        self.handshake()
    
    
    def handshake(self):
        self.timestamp = self.createTimestamp()
        self.authenticationCode = self.createAuthenticationCode()
        self.url += r"/?" +self.encodeUrl()
        conn = urllib2.urlopen(self.url)
        for i in conn.readlines():
            print i        
        
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


