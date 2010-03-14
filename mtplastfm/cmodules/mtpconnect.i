 /* main.i */
 %module mtpconnect
 %{
 /* Put header files here or function declarations like below */
#define SWIG_FILE_WITH_INIT
#include <libmtp.h>
 #include <stdio.h>
 %}
 
extern LIBMTP_mtpdevice_t* get_device();
extern void close_device(LIBMTP_mtpdevice_t *device);
extern char* get_manufacturer(LIBMTP_mtpdevice_t *device);
extern char* get_model(LIBMTP_mtpdevice_t *device);
extern char* get_libmtp_version();
