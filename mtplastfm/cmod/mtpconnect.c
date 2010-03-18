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

LIBMTP_mtpdevice_t* device;
LIBMTP_track_t *current_track, *tmp;
int counter;


int open_device(void)
{
    LIBMTP_Init();
    LIBMTP_error_number_t error;
    error = LIBMTP_Get_Connected_Devices(&device);
    switch(error)
    {
    case(LIBMTP_ERROR_CONNECTING):
        printf("Error connecting\n"); //7
        break;
    case(LIBMTP_ERROR_NO_DEVICE_ATTACHED):
        printf("No Device attached\n"); //5
        break;
    case(LIBMTP_ERROR_GENERAL):
        printf("General error\n");
        break;
    case(LIBMTP_ERROR_PTP_LAYER):
        printf("PTP Layer Error\n");
        break;
    case(LIBMTP_ERROR_USB_LAYER):
        printf("USB Layer Error\n");
        break;
    case(LIBMTP_ERROR_MEMORY_ALLOCATION):
        printf("Memory allocation error\n");
        break;
    case(LIBMTP_ERROR_STORAGE_FULL):
        printf("Error: Storage full\n");
        break;
    case(LIBMTP_ERROR_CANCELLED):
        printf("Connection cancelled\n");
        break;
    case(LIBMTP_ERROR_NONE):
        printf("Successfully connected\n");
        break;
    }
    return error;
}


void close_device(void)
{
    if(device != NULL)
        LIBMTP_Release_Device(device);
    else
        printf("No pointer to device found\n");
}

int reset_device(void)
{
    if(device != NULL)
        return LIBMTP_Reset_Device(device);
    else
        printf("No pointer to device found\n");
    return 1;
}

LIBMTP_mtpdevice_t* next_device(void)
{
    device = device->next;
    return device;
}


char* get_manufacturer(void)
{
    return LIBMTP_Get_Manufacturername(device);
}

char* get_model(void)
{
    return LIBMTP_Get_Modelname(device);
}

char* get_libmtp_version(void)
{
    return LIBMTP_VERSION_STRING;
}

LIBMTP_track_t* get_tracks(void)
{
    counter = 0;
    current_track = LIBMTP_Get_Tracklisting_With_Callback(device, NULL, NULL);
    //count tracks
    //is this a good idea, it may waste time on large collections
    tmp = current_track;
    while(tmp != NULL)
    {
        counter++;
        tmp = tmp->next;
    }
    return current_track;
}

int get_track_count(void)
{
    return counter;
}

LIBMTP_track_t* next_track(void)
{
    LIBMTP_track_t* tmp;
    tmp = current_track;
    current_track = current_track->next;
    LIBMTP_destroy_track_t(tmp);
    return current_track;
}

char* get_friendly_name(void)
{
    return LIBMTP_Get_Friendlyname(device);
}

char* get_artist(void)
{
    return current_track->artist;
}

char* get_title(void)
{
    return current_track->title;
}

char* get_album(void)
{
    return current_track->album;
}

int get_duration(void)
{
    //return in seconds and make it 3minutes long if this attribute is missing
    //otherwise last.fm wont scrobble it.
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
    //return as a char that can be sent straight to last.fm
    if(current_track->rating == 99)
        return "L";
    if(current_track->rating == 1)
        return "B";
    return "";
}

int get_track_number(void)
{
    return current_track->tracknumber;
}

int get_usecount(void)
{
    return current_track->usecount;
}

int is_valid_track(void)
{
    //check if this is a valid track and sets the error string variable if it isnt
    //a valid track must contain at least:
    // artist/title/acceptable filetype

    if(! LIBMTP_FILETYPE_IS_AUDIO(current_track->filetype))
        return 1;
    if(current_track->title == NULL || current_track->title == "")
        return 3;
    if(current_track->artist == NULL || current_track->artist == "")
        return 2;
    return 0;

}

