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

extern int open_device();
extern void close_device();
extern int reset_device();
extern char* get_manufacturer();
extern char* get_model();
extern char* get_libmtp_version();
extern LIBMTP_track_t* get_tracks();
extern int get_track_count();
extern LIBMTP_track_t* next_track();

extern char* get_artist();
extern char* get_title();
char* get_album();
int get_duration();
int get_item_id();
char* get_rating();
int get_track_number();
int get_usecount();

int is_valid_track();
char* get_invalid_track_string();


