/* Boodler: a programmable soundscape tool
   Copyright 2007-2011 by Andrew Plotkin <erkyrath@eblong.com>
   Boodler web site: <http://boodler.org/>
   The cboodle_stdout extension is distributed under the LGPL.
   See the LGPL document, or the above URL, for details.
*/

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <wchar.h>

#include "common.h"
#include "audev.h"

#define DEFAULT_SOUNDRATE (44100)

static FILE* device = NULL;
static long sound_rate = 0; /* frames per second */
static int sound_channels = 0;
static long sound_buffersize = 0; /* bytes */

static long samplesperbuf = 0;
static long framesperbuf = 0;

static char* rawbuffer = NULL;
static long* valbuffer = NULL;

int audev_init_device(char* devname,
                      long ratewanted,
                      int verbose,
                      extraopt_t* extra) {
  int channels, format, rate;
  int fragsize;
  extraopt_t* opt;

  if (verbose) {
    fprintf(stderr, "Boodler: STDOUT sound driver.\n");
  }

  if (device) {
    fprintf(stderr, "Sound device is already open.\n");
    return FALSE;
  }

  format = -1;

  for (opt = extra; opt->key; opt++) {
    if (!wcscmp(opt->key, L"listdevices")) {
      fprintf(stderr, "Device list: not applicable.\n");
    }
  }

  if (!ratewanted) {
    ratewanted = DEFAULT_SOUNDRATE;
  }

  device = stdout;

  if (verbose) {
    fprintf(stderr, "Writing to stdout...\n");
  }

  rate = ratewanted;
  channels = 2;
  fragsize = 16384;

  if (verbose) {
    fprintf(stderr,
            "%d channels, %d frames per second, 16-bit samples (signed, "
            "little-endian)\n",
            channels, rate);
  }

  sound_rate = rate;
  sound_channels = channels;
  sound_buffersize = fragsize;

  samplesperbuf = sound_buffersize / 2;
  framesperbuf = sound_buffersize / (2 * sound_channels);

  rawbuffer = (char*)malloc(sound_buffersize);
  if (!rawbuffer) {
    fprintf(stderr, "Unable to allocate sound buffer.\n");
    device = NULL;
    return FALSE;
  }

  valbuffer = (long*)malloc(sizeof(long) * samplesperbuf);
  if (!valbuffer) {
    fprintf(stderr, "Unable to allocate sound buffer.\n");
    free(rawbuffer);
    rawbuffer = NULL;
    device = NULL;
    return FALSE;
  }

  return TRUE;
}

void audev_close_device() {
  if (device == NULL) {
    fprintf(stderr, "Unable to close sound device which was never opened.\n");
    return;
  }

  device = NULL;

  if (rawbuffer) {
    free(rawbuffer);
    rawbuffer = NULL;
  }
  if (valbuffer) {
    free(valbuffer);
    valbuffer = NULL;
  }
}

long audev_get_soundrate() {
  return sound_rate;
}

long audev_get_framesperbuf() {
  return framesperbuf;
}

int audev_loop(mix_func_t mixfunc, generate_func_t genfunc, void* rock) {
  char* ptr;
  int ix, res;

  if (!device) {
    fprintf(stderr, "Sound device is not open.\n");
    return FALSE;
  }

  while (1) {
    res = mixfunc(valbuffer, genfunc, rock);

    if (res) {
      return TRUE;
    }

    for (ix = 0, ptr = rawbuffer; ix < samplesperbuf; ix++) {
      long samp = valbuffer[ix];

      if (samp > 0x7FFF) {
        samp = 0x7FFF;
      } else if (samp < -0x7FFF) {
        samp = -0x7FFF;
      }

      *ptr++ = ((samp)&0xFF);
      *ptr++ = ((samp >> 8) & 0xFF);
    }

    fwrite(rawbuffer, 1, sound_buffersize, device);
  }
}
