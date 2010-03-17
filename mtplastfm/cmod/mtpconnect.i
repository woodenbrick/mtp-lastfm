//Copyright 2010 Daniel Woodhouse
//
//This file is part of mtp-lastfm.
//
//mtp-lastfm is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or
//(at your option) any later version.
//
//mtp-lastfm is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with mtp-lastfm.  If not, see http://www.gnu.org/licenses/

 %module mtpconnect
 %{
#define SWIG_FILE_WITH_INIT
#include <libmtp.h>
 #include <stdio.h>
 %}

extern int open_device(void);
extern void close_device(void);
extern int reset_device(void);
extern char* get_manufacturer(void);
extern char* get_model(void);
extern char* get_libmtp_version(void);
extern LIBMTP_track_t* get_tracks(void);
extern int get_track_count(void);
extern LIBMTP_track_t* next_track(void);

extern char* get_artist(void);
extern char* get_title(void);
char* get_album(void);
int get_duration(void);
int get_item_id(void);
char* get_rating(void);
int get_track_number(void);
int get_usecount(void);

int is_valid_track(void);


