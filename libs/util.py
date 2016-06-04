#!/usr/bin/env python

import os, sys
import time
from xapi.storage.common import call
from xapi.storage import log
import xml.dom.minidom
import fcntl
import errno

RETRY_MAX = 20 # retries
RETRY_PERIOD = 1.0 # seconds

#Opens and locks a file, returns filehandle
def try_lock_file(dbg, filename, mode="a+"):
    try:
        f = open(filename, mode)
    except:
        raise xapi.storage.api.volume.Unimplemented(
                  "Couldn't open refcount file: %s" % filename)
    retries = 0
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except IOError as e:
            # raise on unrelated IOErrors
            if e.errno != errno.EAGAIN:
                raise

        if retries >= RETRY_MAX:
            raise xapi.storage.api.volume.Unimplemented(
                  "Couldn't lock refcount file: %s" % filename)
        time.sleep(RETRY_PERIOD)

    return f


def lock_file(dbg, filename, mode="a+"):
    f = open(filename, mode)
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


#Unlocks and closes file
def unlock_file(dbg, filehandle):
    fcntl.flock(filehandle, fcntl.LOCK_UN)
    filehandle.close()