#include <libmtp.h>
#include <stdio.h>


LIBMTP_mtpdevice_t* get_device()
{
    LIBMTP_Init();
    LIBMTP_mtpdevice_t* device;
    LIBMTP_error_number_t error;
    error = LIBMTP_Get_Connected_Devices(&device);
    switch(error)
    {
    case(LIBMTP_ERROR_CONNECTING):
        printf("Error connecting\n");
        break;
    case(LIBMTP_ERROR_NO_DEVICE_ATTACHED):
        printf("No Device attached\n");
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
    if(error == LIBMTP_ERROR_NONE)
        return device;
    else
        return NULL;
}



void close_device(LIBMTP_mtpdevice_t *device)
{
    LIBMTP_Release_Device(device);
}

char* get_manufacturer(LIBMTP_mtpdevice_t *device)
{
    return LIBMTP_Get_Manufacturername(device);
}

char* get_model(LIBMTP_mtpdevice_t *device)
{
    return LIBMTP_Get_Modelname(device);
}

char* get_libmtp_version()
{
    return LIBMTP_VERSION_STRING;
}

