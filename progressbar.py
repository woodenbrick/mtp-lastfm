#!/usr/bin/env python

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

import gtk
import pygtk
import gobject

class ProgressBar(object):
    def __init__(self, progress_bar, max_value, start_value, update_speed=300):
        self.progress_bar = progress_bar
        self.current_progress = start_value
        self.max_value = max_value
        self.progress_bar.set_fraction(start_value)
        self.progress_bar.show()
        self.timer = gobject.timeout_add(update_speed, self.run_timer)
        
    def run_timer(self, finished=False):
        """Updates the progress bar"""
        if finished:
            self.timer2 = gobject.timeout_add(1000, self.hide_progress)
            return
        
        fraction = self.current_progress / float(self.max_value)
        if fraction >= 0 and fraction <= 1:
            self.progress_bar.set_fraction(fraction)
        return True
    
    def hide_progress(self):
        self.progress_bar.hide()
        gobject.source_remove(self.timer)
        gobject.source_remove(self.timer2)
        self.timer = 0
        self.timer2 = 0