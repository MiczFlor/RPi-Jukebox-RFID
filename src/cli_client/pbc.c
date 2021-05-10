/**
  \file pbc.c

    MIT License

    Copyright (C) 2021 Arne Pagel

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
*/

/*

    pbc -> PhonieBox Command line interface

    depenmds on libczmq:
    apt-get install libczmq-dev

    how to compile:
    gcc pbc.c -o pbc -lzmq -Wall

*/

#include <getopt.h>
#include <czmq.h>

#define MAX_STRLEN 256
#define MAX_REQEST_STRLEN  (MAX_STRLEN * 16)
#define MAX_PARAMS 16
int g_verbose = 0;

typedef struct 
{
    char object [MAX_STRLEN];
    char method [MAX_STRLEN];
    char params [MAX_PARAMS][MAX_STRLEN];
    int num_params;
} t_request;


int send_zmq_request_and_wait_response(char * request, int request_len, char * response, int max_response_len)
{
    int zmq_ret,ret = -1;
    void *context = zmq_ctx_new ();
    void *requester = zmq_socket (context, ZMQ_REQ);
    int linger = 200;
    zmq_setsockopt(requester,ZMQ_LINGER,&linger,sizeof(linger));
    zmq_setsockopt(requester,ZMQ_RCVTIMEO,&linger,sizeof(linger));
    zmq_connect (requester, "tcp://localhost:5555");

    zmq_ret = zmq_send (requester, request, request_len, 0);

    if (zmq_ret > 0)
    {
        zmq_ret = zmq_recv (requester, response, max_response_len, 0);
        
        if (zmq_ret > 0)
        {
            printf ("Received %s (%d Bytes)\n", response,zmq_ret);    
            ret = 0;
        }
        else
        {
            printf ("zmq_recv rturned %d \n", zmq_ret);    
        }
    }
    else
    {
      if (g_verbose) printf ("zmq_send returned %d\n", zmq_ret);  
    }

    zmq_close (requester);
    zmq_ctx_destroy (context); 
    return (ret);
}


void * connect_and_send_request(t_request * tr)
{
    char json_request[MAX_REQEST_STRLEN];
    char json_response[MAX_REQEST_STRLEN];
    char params[MAX_STRLEN * 8];
    size_t json_len;
    int n;

    if (tr->num_params > 0)
    {
        sprintf(params, "\"params\":{");
        
        for (n = 0;n < tr->num_params;)
        {
            strcat(params,tr->params[n]);
            n++;
            if (n < tr->num_params) strcat(params,",");
        }

        strcat(params,"},");

    }
    else params[0] = 0;

    snprintf(json_request,MAX_REQEST_STRLEN,"{\"object\": \"%s\", \"method\": \"%s\", %s\"id\":%d}",tr->object,tr->method,params,123);
    json_len = strlen(json_request);
    
    if (g_verbose) printf("Sending Request (%ld Bytes):\n%s\n",json_len,json_request);

    send_zmq_request_and_wait_response(json_request,json_len,json_response,MAX_REQEST_STRLEN);

    return 0;
}

int check_and_map_parameters_to_json(char * arg, t_request * tr)
{
    char * name;
    char * value;
    char * fmt;
    int ret = 0;
    if (strchr(arg, ':') != NULL)
    {
        name = strtok(arg, ":");
        value = strtok(NULL, ":");
        fmt = (isdigit(*value)) ? "\"%s\":%s"  : "\"%s\":\"%s\"";
        snprintf (tr->params[tr->num_params++],MAX_STRLEN, fmt,name,value);
        ret = 1;
    }
    return (ret);
}


void usage(void)
{
    fprintf(stderr,"\npbc -> PhonieBox Command line interface\nusage: pbc -o object -m method param_name:value\n\n");
    fprintf(stderr,"    -h this screen\n");
    fprintf(stderr,"    -o, --object object\n");
    fprintf(stderr,"    -m, --method method\n");
    fprintf(stderr,"    -v verbose\n");

    fprintf(stderr,"last change %s\n\n",__DATE__);
    exit (1);
}

/**
   returns the index of the first argument that is not an option; i.e.
   does not start with a dash or a slash
*/
int HandleOptions(int argc,char *argv[], t_request * tr)
{
  int c;
  
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

      case 'v':
        g_verbose = '1';
        break;

      default:
        usage();
        abort ();
    }
  }

  /* treat remaining command line arguments (not options). */
  if (optind < argc)
  {
    while (optind < argc)
    { 
        check_and_map_parameters_to_json(argv[optind++], tr);
    }
  }

  return (1);
}

int main(int argc,char *argv[])
{
    t_request tr;

    bzero(&tr, sizeof(t_request));

    HandleOptions(argc,argv,&tr);
    connect_and_send_request(&tr);
    
    return 0;
}
