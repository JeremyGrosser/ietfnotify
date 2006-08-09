# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details


import sys
import syslog
import ietfnotify.config as conf

# Constants
DEBUG = 'DEBUG'
ERROR = 'ERROR'
INFO = 'INFO'
NETWORK = 'NETWORK'

class LogStream:
	def __init__(self, f):
		self.f = f
	def write(self, s):
		self.f.write(s)
		self.f.flush()

# ----------------------------------------------------------------------
# Utility functions

def getconfigfacility():
    facilitymap = { 
	"user":     syslog.LOG_USER,
	"mail":     syslog.LOG_MAIL,
	"daemon":   syslog.LOG_DAEMON,
	"auth":     syslog.LOG_AUTH,
	"lpr":      syslog.LOG_LPR,
	"news":     syslog.LOG_NEWS,
	"uucp":     syslog.LOG_UUCP,
	"cron":     syslog.LOG_CRON,
	"local0":   syslog.LOG_LOCAL0,
	"local1":   syslog.LOG_LOCAL1,
	"local2":   syslog.LOG_LOCAL2,
	"local3":   syslog.LOG_LOCAL3,
	"local4":   syslog.LOG_LOCAL4,
	"local5":   syslog.LOG_LOCAL5,
	"local6":   syslog.LOG_LOCAL6,
	"local7":   syslog.LOG_LOCAL7,
        }
    try:
        facility = conf.get("logging", "facility")
    except:
        facility = "user"
    return facilitymap.get(facility, syslog.LOG_USER)


def getconfigpriority():
    #LOG_EMERG, LOG_ALERT, LOG_CRIT, LOG_ERR, LOG_WARNING, LOG_NOTICE,
    #LOG_INFO, LOG_DEBUG.
    prioritymap = { 
#	"user":     syslog.LOG_USER,
	"emerg":	syslog.LOG_EMERG, 
	"emergency":	syslog.LOG_EMERG, 
	"alert":	syslog.LOG_ALERT, 
	"crit":         syslog.LOG_CRIT, 
	"critical":	syslog.LOG_CRIT, 
	"err":          syslog.LOG_ERR, 
	"error":	syslog.LOG_ERR, 
	"warn":         syslog.LOG_WARNING, 
	"warning":	syslog.LOG_WARNING, 
	"notice":	syslog.LOG_NOTICE, 
	"info":         syslog.LOG_INFO, 
	"debug":	syslog.LOG_DEBUG, 
        }
    try:
        priority = conf.get("logging", "priority")
    except:
        priority = "info"
    return prioritymap.get(priority, syslog.LOG_INFO)


# ----------------------------------------------------------------------

syslog.openlog("ietfnotify", syslog.LOG_PID, getconfigfacility())
syslog.setlogmask(syslog.LOG_UPTO(getconfigpriority()))

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

def cleanup():
    pass


