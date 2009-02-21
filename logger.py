# Copyright 2009 Daniel Woodhouse
#
#This file is part of mtp-lastfm.
#
#mtp-lastfm is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Foobar is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with mtp-lastfm.  If not, see http://www.gnu.org/licenses/

import logging

class Logger:
    def __init__(self, name = 'log', file_log = True, stream_log = True,
                 logger_level = logging.DEBUG, file_log_name = 'error.log',
                 file_log_level = 2, stream_log_level = 3):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logger_level)
        format_detailed = logging.Formatter("%(asctime)s - %(name)s - %(message)s\n")
        format_message = logging.Formatter("%(message)s")
        if file_log:
            fh = logging.FileHandler(file_log_name)
            fh.setLevel(self.get_log_level(file_log_level))
            fh.setFormatter(format_detailed)
            self.logger.addHandler(fh)
        if stream_log:
            sl = logging.StreamHandler()
            sl.setLevel(self.get_log_level(stream_log_level))
            sl.setFormatter(format_message)
            self.logger.addHandler(sl)

    def get_log_level(self, num):
        levels = [logging.DEBUG, logging.INFO, logging.WARN, logging.CRITICAL]
        return levels[num-1]