import sqlite3
import httplib
import md5
import time
import urllib
import urllib2
import string

#c = sqlite3.Connection('./lastfm')
#cursor = c.cursor()
#cursor.execute('SELECT songs.*, scrobble.scrobbles FROM songs INNER JOIN scrobble ON songs.trackid=scrobble.trackid')
#for i in cursor:
#    print i

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
        response = conn.readline().strip()
        print response
        if response == 'OK':
            print 'Server response OK.'
            self.sessionID = conn.readline().strip
            self.nowPlayingUrl = conn.readline().strip #not used at this time
            self.submissionUrl = conn.readline().strip
        elif response == 'BADAUTH':
            print 'user details incorrect'
        elif response == 'BANNED':
            print 'this scrobbling client has been banned from submission, please notify the developer'
        elif response == 'BADTIME':
            print 'timestamp is incorrect, please check your clock settings'
        elif response.startswith('FAILED'):
            print 'Connection to server failed:', string.split(response, ' ')[1:]
        
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
    scrobbler = Scrobbler('woodenbrck', password)
    
if __name__ == '__main__':
    run()


