# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details


import sys
import syslog

# Constants
DEBUG = 'DEBUG'
ERROR = 'ERROR'
INFO = 'INFO'
NETWORK = 'NETWORK'
debugMode = False

class LogStream:
	def __init__(self, f):
		self.f = f
	def write(self, s):
		self.f.write(s)
		self.f.flush()

# ----------------------------------------------------------------------

syslog.openlog("ietfnotify", syslog.LOG_PID, syslog.LOG_USER)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

def debug(msg):
    syslog.syslog(syslog.LOG_DEBUG, msg)
def info(msg):
    syslog.syslog(syslog.LOG_INFO, msg)
def note(msg):
    syslog.syslog(syslog.LOG_NOTICE, msg)
def warn(msg):
    syslog.syslog(syslog.LOG_WARNING, msg)
def err(msg):
    syslog.syslog(syslog.LOG_ERR, msg)

# ---- compatibility function ----

def log(pri, msg):
    if pri == DEBUG:
        debug(msg)
    if pri == INFO:
        info(msg)
    if pri == NETWORK:
        warn(msg)
    if pri == ERROR:
        err(msg)
	if debugMode:
		print msg

def cleanup():
    pass
    
