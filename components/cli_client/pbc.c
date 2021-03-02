/**
  \file rfg.c

  rfg cli and main

  Copyright (C) 2008 Arne Pagel <arne@pagelnet.de>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <getopt.h>


//#include <ctype.h>

#include <czmq.h>

//apt-get install libczmq-dev

// build this gcc pbc.c -o pbc -lzmq  

#define MAX_STRLEN 256
#define MAX_REQEST_STRLEN  (MAX_STRLEN * 3) + 256

int g_verbose = 0;


typedef struct 
{
    char object [MAX_STRLEN];
    char method [MAX_STRLEN];
    char params [MAX_STRLEN];
} t_request;

void * connect_and_send_request(t_request * tr)
{
    char json_request[MAX_REQEST_STRLEN];
    size_t json_len;
    printf ("Connecting to hello world server…\n");

    
    
    /*printf ("object %s'\n", tr->object);
    printf ("object %s'\n", tr->method);
    printf ("object %s'\n", tr->params);*/

    snprintf(json_request,MAX_REQEST_STRLEN,"{\"OBJECT\": %s, \"METHOD\": %s, \"PARAMS\": {%s},\"id\":%d}",tr->object,tr->method,tr->params,123);
    json_len = strlen(json_request);

    
    if (g_verbose) printf("Sending Request (%ld Bytes):\n%s\n",json_len,json_request);

    void *context = zmq_ctx_new ();
    void *requester = zmq_socket (context, ZMQ_REQ);

    
    zmq_connect (requester, "tcp://localhost:5555");

    zmq_send (requester, json_request, json_len, 0);
    //zmq_recv (requester, buffer, 10, 0);
    //printf ("Received World %d\n", request_nbr);

    zmq_close (requester);
    zmq_ctx_destroy (context);
    return 0;
}




void usage(void)
{
    fprintf(stderr,"\nusage: rfg -i inputfile -o outputfile -t outpufiletype\n\n");
    //fprintf(stderr,"    -b startsegment for firmwarefile\n");
    //fprintf(stderr,"    -c generate crc checksum struct within the firmware at 0x0C10200 \n");
    fprintf(stderr,"    -d swtich debugmesages on\n");
    fprintf(stderr,"    -h this screen\n");
    fprintf(stderr,"    -i input firmware-file\n");
    //fprintf(stderr,"    -l fpga-file\n");

    //fprintf(stderr,"    -f outputformat\n");
    //fprintf(stderr,"    -g gui-override, displays a dialog wich is asking you what to do\n");

    //fprintf(stderr,"    -n create name.txt, a file with version and date\n");
    //fprintf(stderr,"    -s create sw_info struct (only with -c)\n");
    fprintf(stderr,"    -t Outfiletype: e = elf, h = ihex, \n");

    fprintf(stderr,"    -v verbose\n");
    //fprintf(stderr,"    -x generate intel hex format (128 byte per row)\n");
    //fprintf(stderr,"    -z compress-firmware (default without compression)\n");

    fprintf(stderr,"\nrfg, written by Arne Pagel 01.Feb.2007\n");
    fprintf(stderr,"last change %s\n\n",__DATE__);
    exit (1);
}

/**
   returns the index of the first argument that is not an option; i.e.
   does not start with a dash or a slash
*/
int HandleOptions(int argc,char *argv[], t_request * tr)
{
  int i,c,firstnonoption=0;
  int oft_cnt = 0,of_cnt = 0;

  const struct option long_options[] =
  {
    /* These options set a flag. */
    //{"verbose", no_argument,       &verbose_flag, 1},
    //{"brief",   no_argument,       &verbose_flag, 0},
    /* These options don't set a flag.
    We distinguish them by their indices. */
    {"help",        no_argument,       0, 'h'},
    {"object",      required_argument, 0, 'o'},
    {"method",      required_argument, 0, 'm'},
    {"params",      optional_argument, 0, 'p'},
    {0, 0, 0, 0}
  };

  const char short_options[] = {"o:m:p:?hv"};

  while (1)
  {
    int option_index = 0;     // getopt_long stores the option index here.

    c = getopt_long (argc, argv,short_options,long_options, &option_index);

    // Detect the end of the options.
    if (c == -1) break;

    switch (c)
    {
      case '?':
      case 'h':
        usage();
        puts ("option -a\n");
        break;

      case 'o':
        strncpy (tr->object,optarg,MAX_STRLEN);
        break;

      case 'm':
        strncpy (tr->method,optarg,MAX_STRLEN);
        break;

      case 'p':
        strncpy (tr->params,optarg,MAX_STRLEN);
        break;

      case 'v':
        g_verbose = '1';
        break;

      default:
        usage();
        abort ();
    }
  }

  /* Print any remaining command line arguments (not options). */
  if (optind < argc)
  {
    printf ("non-option ARGV-elements: ");
    while (optind < argc) printf ("%s ", argv[optind++]);
    putchar ('\n');
  }

  return firstnonoption;
}



#ifdef WIN32
  #include "windows.h"
#endif 

#define CC_BLACK  0
#define CC_BLUE   1
#define CC_RED    2

void set_color(int color)
{
  #ifdef WIN32
    int w_col;
    HANDLE hConsole;
    static CONSOLE_SCREEN_BUFFER_INFO ConsoleInfo;
    hConsole = GetStdHandle(STD_OUTPUT_HANDLE);  // Get handle to standard output
    static int init;
    
    if (init == 0)
    {
      init = 1;
      GetConsoleScreenBufferInfo(hConsole, &ConsoleInfo);
    }

    switch (color)
    {
      case CC_BLACK:
        w_col = ConsoleInfo.wAttributes;
        break;
      case CC_BLUE:
        w_col = FOREGROUND_BLUE | FOREGROUND_INTENSITY;
        break;
      case CC_RED:
        w_col = FOREGROUND_RED | FOREGROUND_INTENSITY;
        break;
    }
    SetConsoleTextAttribute(hConsole,w_col);  // set the text attribute of the previous handle
  #else
    switch (color)
    {
      case CC_BLACK:
        printf ("\033[0;00m");
        break;
      case CC_BLUE:
        printf ("\033[1;34m");
        break;
      case CC_RED:
        printf ("\033[1;33m");
        break;
    }
  #endif
}



int main(int argc,char *argv[])
{
    time_t timestamp;
    struct tm * tmtime;
    t_request tr;

    bzero(&tr, sizeof(t_request));




//t_data_sec_descriptor sd;

    //Zeitstempel holen
    time(&timestamp);

    //Zeitstempel konvertieren
    tmtime = localtime(&timestamp);

    //Programmoptionen interpretieren
    HandleOptions(argc,argv,&tr);

    connect_and_send_request(&tr);

    return 0;
}
