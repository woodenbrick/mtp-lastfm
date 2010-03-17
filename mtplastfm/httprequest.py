# Copyright 2009 Daniel Woodhouse
#
#This file is part of mtp-lastfm.
#
#mtp-lastfm is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#mtp-lastfm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with mtp-lastfm.  If not, see http://www.gnu.org/licenses/
import urllib
import urllib2
import socket
import httplib
import threading
import localisation
import Queue
import gtk

_ = localisation.set_get_text()

class HttpRequest(object):
    """Timeout a request to last.fm if its taking too long python<2.5 doesnt have
    a param for this in the urlopen method"""
    def __init__(self, url, data=None, timeout=15):
        self.request = urllib2.Request(url, data)
        socket.setdefaulttimeout(timeout)
        self.queue = Queue.Queue()
        self.response = None
        self.finished = False

    def retrieve(self, url, filename, thumb_widget):
        conn = threading.Thread(target=self._retrieve, args=[url, filename, thumb_widget])
        conn.daemon = True
        conn.start()
            
    def _retrieve(self, url, filename, thumb_widget):
        urllib.urlretrieve(url, filename)
        image = gtk.gdk.pixbuf_new_from_file_at_size(filename, 100, 40)
        thumb_widget.set_from_pixbuf(image)

        
    def connect(self, xml=False):
        conn = threading.Thread(target=self._connect, args=[xml])
        conn.daemon = True
        conn.start()
        self.response = self.queue.get()
        self.finished = True
        return self.response
        
    def _connect(self, xml=False):
        """Connects to last.fm returns a tuple (bool connection_success, str msg)"""
        response = []
        try:
            conn = urllib2.urlopen(self.request)
            if xml:
                self.queue.put(conn)
                return
            for line in conn.readlines():
                response.append(line.strip())
            if response[0] == "OK":
                self.queue.put((True, response))
                return
        except urllib2.URLError, error:
             response.append(error)
        except httplib.BadStatusLine:
             response = response.append("Bad status line")
        if xml:
            self.queue.put(False)
        else:
            self.queue.put((False, response))


    def handshake_response(self, response):
        responses = {
            "OK" : _("User authenticated"),
            "BADAUTH" : _("Username or password incorrect, please reset"),
            "BANNED" : _("""This scrobbling client has been banned from submission, please notify the developer"""),
            "BADTIME" : _("Timestamp is incorrect, please check your clock settings"),
            "FAILED" : response
        }
        try:
            return responses[response]
        except KeyError:
            return response

