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
    def __init__(self, progress_bar):
        self.progress_bar = progress_bar
        self.progress_bar.set_pulse_step(0.03)
        self.progress_bar.set_text("")
    
    def set_vars(self, max_value=100, start_value=0, update=100, pulse_mode=False,
                 text=""):
        self.update_speed = update
        self.current_progress = start_value
        self.max_value = max_value
        self.pulse_mode = pulse_mode
        self.progress_bar.set_text(text)
        self.progress_bar.set_fraction(start_value)

        
    def run_timer(self):
        """Updates the progress bar"""
        if self.max_value == 0:
            return
        if self.pulse_mode:
            self.progress_bar.pulse()
            return True
        fraction = self.current_progress / float(self.max_value)
        if fraction >= 0 and fraction <= 1:
            self.progress_bar.set_fraction(fraction)
        return True
    
    
    def start(self):
        self.progress_bar.show()
        self.timer = gobject.timeout_add(self.update_speed, self.run_timer)
        
    
    def delayed_stop(self, delay):
        """For those times when we want the progress bar to hang around a lil bit longer"""
        gobject.source_remove(self.timer)
        self.progress_bar.set_fraction(1)
        self.timer = gobject.timeout_add(delay, self.stop)
    
        
    def stop(self):
        self.progress_bar.hide()
        self.progress_bar.set_text("")
        gobject.source_remove(self.timer)

