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

#include <libmtp.h>
#include <stdio.h>
#include "mtpconnect.h"
int open_device(void)
{
    fprintf(stderr, "Opening device");
    LIBMTP_Init();
    LIBMTP_error_number_t error;
    error = LIBMTP_Get_Connected_Devices(&device);
    switch(error)
    {
    case(LIBMTP_ERROR_CONNECTING):
        fprintf(stderr, "Error connecting\n"); //7
        break;
    case(LIBMTP_ERROR_NO_DEVICE_ATTACHED):
        fprintf(stderr, "No Device attached\n"); //5
        break;
    case(LIBMTP_ERROR_GENERAL):
        fprintf(stderr, "General error\n");
        break;
    case(LIBMTP_ERROR_PTP_LAYER):
        fprintf(stderr, "PTP Layer Error\n");
        break;
    case(LIBMTP_ERROR_USB_LAYER):
        fprintf(stderr, "USB Layer Error\n");
        break;
    case(LIBMTP_ERROR_MEMORY_ALLOCATION):
        fprintf(stderr, "Memory allocation error\n");
        break;
    case(LIBMTP_ERROR_STORAGE_FULL):
        fprintf(stderr, "Error: Storage full\n");
        break;
    case(LIBMTP_ERROR_CANCELLED):
        fprintf(stderr, "Connection cancelled\n");
        break;
    case(LIBMTP_ERROR_NONE):
        fprintf(stderr, "Successfully connected\n");
        break;
    }
    return error;
}


void close_device(void)
{
    if(device != NULL)
    {
        fprintf(stderr, "Closing device\n");
        LIBMTP_Release_Device(device);
    }
    else
        fprintf(stderr, "No pointer to device found\n");
}

int reset_device(void)
{
    if(device != NULL)
        return LIBMTP_Reset_Device(device);
    else
        fprintf(stderr, "No pointer to device found\n");
    return 1;
}

LIBMTP_mtpdevice_t* next_device(void)
{
    device = device->next;
    return device;
}


char* get_manufacturer(void)
{
    fprintf(stderr, "getting manufacturer\n");
    return LIBMTP_Get_Manufacturername(device);
}

char* get_model(void)
{
    fprintf(stderr, "getting model\n");
    return LIBMTP_Get_Modelname(device);
}

char* get_libmtp_version(void)
{
    return LIBMTP_VERSION_STRING;
}

LIBMTP_track_t* get_tracks(void)
{
    fprintf(stderr, "getting track listing\n");
    counter = 0;
    current_track = LIBMTP_Get_Tracklisting_With_Callback(device, NULL, NULL);
    //count tracks
    //is this a good idea, it may waste time on large collections
    fprintf(stderr, "tracks aqcuired, running count");
    tmp = current_track;
    while(tmp != NULL)
    {
        counter++;
        tmp = tmp->next;
    }
    fprintf(stderr, "Count: %d\n", counter);
    return current_track;
}

int get_track_count(void)
{
    return counter;
}

LIBMTP_track_t* next_track(void)
{
    fprintf(stderr, "Getting next track\n");
    LIBMTP_track_t* tmp;
    tmp = current_track;
    current_track = current_track->next;
    LIBMTP_destroy_track_t(tmp);
    return current_track;
}

char* get_friendly_name(void)
{
    fprintf(stderr, "Getting friendly name\n");
    return LIBMTP_Get_Friendlyname(device);
}

char* get_artist(void)
{
    fprintf(stderr, "Getting artist\n");
    return current_track->artist;
}

char* get_title(void)
{
    fprintf(stderr, "Getting title\n");
    return current_track->title;
}

char* get_album(void)
{
    fprintf(stderr, "Getting album\n");
    return current_track->album;
}

int get_duration(void)
{
    //return in seconds and make it 3minutes long if this attribute is missing
    //otherwise last.fm wont scrobble it.
    fprintf(stderr, "Getting duration\n");
    if (current_track->duration == 0)
        return 180;
    return current_track->duration / 1000;
}


int get_item_id(void)
{
    return current_track->item_id;
}

char get_rating(void)
{
    fprintf(stderr, "Getting rating\n");
    //return as a char that can be sent straight to last.fm
    if(current_track->rating == 99)
        return 'L';
    if(current_track->rating == 1)
        return 'B';
    return ' ';
}

int get_track_number(void)
{
    return current_track->tracknumber;
}

int get_usecount(void)
{
    fprintf(stderr, "getting usecount\n");
    fflush(1);
    return current_track->usecount;
}

int is_valid_track(void)
{
    //check if this is a valid track and sets the error string variable if it isnt
    //a valid track must contain at least:
    // artist/title/acceptable filetype
    fprintf(stderr, "checking is valid filetype\n");

    if(! LIBMTP_FILETYPE_IS_AUDIO(current_track->filetype))
        return 1;
    if(current_track->title == NULL)
        return 3;
    if(current_track->artist == NULL) 
        return 2;
    return 0;

}

