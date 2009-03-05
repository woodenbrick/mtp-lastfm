#!/usr/bin/env python

class LastfmWebService(object):
    
    def __init__(self):
        self.api_key = "2d21a4ab6f049a413eb27dbf9af10579"
        self.api_2 = "6146d36f59da8720cd5f3dd2c8422da0"
    
    def request_session_token(self):
        """opens a browser window to request permission from user to love their tracks"""
        api_sig = self.create_api_sig("api_key"+self.api_key+"method"+"auth.gettoken")
        data = [("api_key", self.api_key),
            ("method", "auth.gettoken"),
            ("api_sig", api_sig)]
        encoded_data = urllib.urlencode(data)
        url = "http://ws.audioscrobbler.com/2.0/?" + encoded_data
        conn = urllib2.urlopen(url)
        return self.parse_xml(conn, "token")

    def parse_xml(self, conn, tag):
        """Searches an XML document for a tag and returns its value"""
        tree = ET.parse(conn)
        iter = tree.getiterator()
        for child in iter:
            if child.tag == tag:
                token = child.text
                break
        return token
        
        
    def create_api_sig(self, data):
        """args is a tuple of parmameters [0] param_name [1] value
        send in alphabetial order"""
        data += self.api_2
        api_sig = md5.new(data.encode('UTF-8')).hexdigest()
        return api_sig
    
    
    def request_authorisation(self, token):
        """Opens a browser to request users authentication"""
        encoded_values = urllib.urlencode((
            ("api_key", self.api_key),
            ("token", token)
            ))
        webbrowser.open("http://www.last.fm/api/auth/?" + encoded_values)
        
        
    def create_web_service_session(self, token):
        """The final step, this creates a token with infinite lifespan store in db"""
        api_sig = self.create_api_sig("api_key" + self.api_key + "methodauth.getsessiontoken" + token)
        data = (
            ("api_key", self.api_key),
            ("method", "auth.getsession"),
            ("token", token),
            ("api_sig", api_sig))
        encode_values = urllib.urlencode(data)
        url = "http://ws.audioscrobbler.com/2.0/?" + encode_values
        conn = urllib2.urlopen(url)
        key = self.parse_xml(conn, "key")
        return key
            
    def love_tracks(self, tracks):
        """Love a set of tracks"""
        pass

if __name__ == '__main__':
    webservice = LastfmWebService()
    token = webservice.request_session_token()
    webservice.request_authorisation(token)
    raw_input("Press enter when authorised")
    webservice.create_web_service_session(token)