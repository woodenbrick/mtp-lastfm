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

import os
import gtk
import pygtk
import ID3
import localisation

_ = localisation.set_get_text()

class Tagger(object):
    """Ideally we would be using python bindings for our connection with mtplib
    and if they ever get fixed we should redo this class"""
    
    def __init__(self, glade_file, song_log):
        """song_log is the dict of song(s) that we are going to retag"""
        self.song_log = song_log
        self.temp_dir = os.path.join(os.environ['HOME'], ".mtp-lastfm") + os.sep
        self.wTree = gtk.glade.XML(glade_file)
        self.wTree.signal_autoconnect(self)
        
        self.title = self.wTree.get_widget("title")
        self.artist = self.wTree.get_widget("artist")
        self.album = self.wTree.get_widget("album")
        self.track_number = self.wTree.get_widget("track_number")
        
        self.current_index = 0
        self.total = len(self.song_log)
        self.display_track(self.current_index)
        self.wTree.get_widget("window").show()
    
    def on_previous_clicked(self, widget):
        if self.current_index == 0:
            self.current_index = self.total - 1
        else:
            self.current_index -= 1
        self.display_track(self.current_index)
        
    
    def on_next_clicked(self, widget):
        if self.current_index == self.total - 1:
            self.current_index = 0
        else:
            self.current_index += 1
        self.display_track(self.current_index)
        
    def on_required_info_changed(self, widget):
        """Disable sync button if artist or title are empty"""
        if self.title.get_text() == "" or self.artist.get_text() == "":
            self.wTree.get_widget("sync").set_sensitive(False)
        else:
            self.wTree.get_widget("sync").set_sensitive(True)
  
    
    def display_track(self, index):
        self.wTree.get_widget("counter").set_text(_("Track %(num)d of %(total)d") %
                                                  { "num" : index + 1, "total" : self.total})
        self.title.set_text(self.song_log[index]['Title:'])
        self.artist.set_text(self.song_log[index]['Artist:'])
        self.album.set_text(self.song_log[index]['Album:'])
        self.track_number.set_text(self.song_log[index]['Track number:'])
        self.current_id = self.song_log[index]['Track ID:']
    
    def on_sync_clicked(self, widget):
        self.temp_file = self.temp_dir + str(self.current_id)
        os.system("mtp-getfile %(id)s %(temp_file)s" %
              {'id' : self.current_id, 'temp_file' : self.temp_file})
        #os.system("mtp-delfile -n %s" % self.current_id)
        #it seems like MTP devices don't care about the id3 tags
        #and instead store their own versions of tags
        #we might as well tag the tracks though in case the track is copied from the device
        self.id3 = ID3.ID3(self.temp_file)
        self.fix_tags()
        #mtp-sendtr options:
        #-t <title> -a <artist> -A <Album artist> -w <writer or composer>
        #-l <album> -c <codec> -g <genre> -n <track number> -y <year>
        #-d <duration in seconds> <local path> <remote path>
        #(-q means the program will not ask for missing information.)
        
        #XXX codec is currently set as mp3 however this will have to be changed
        os.system("mtp-sendtr %(source)s -D -t %(title)s -a %(artist)s -A %(artist)s -w Unknown -l %(album)s -c mp3 -g Unknown genre -n %(track_number)s -y 1995 -d %(duration)s" % self.create_tag_dict())
    
    def on_close_clicked(self, widget):
        self.wTree.get_widget("window").destroy()
    
    
    def fix_tags(self):
        """Replace the old tags with user specified"""
        self.id3.artist = self.artist.get_text()
        self.id3.title = self.title.get_text()
        self.id3.album = self.album.get_text()
        self.id3.track = self.track_number.get_text()
        self.id3.write()


    def create_tag_dict(self):
        return {"artist" : self.artist.get_text(),
                "title" : self.title.get_text(),
                "album" : self.album.get_text(),
                "track_number" : self.track_number.get_text(),
                "duration" : self.song_log[self.current_index]["Duration:"],
                "source" : self.temp_file}

    