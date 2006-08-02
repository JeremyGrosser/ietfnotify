# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import logging, time, sys, config

# Constants
DEBUG = 'DEBUG'
ERROR = 'ERROR'
INFO = 'INFO'

#syslog = logging.SysLogHandler()
#syslog.setLevel(logging.ERROR)
#logging.getLogger('').addHandler(syslog)

fd = open(config.get('general', 'logfile'), 'w')

def log(priority, msg):
	#logging.log(priority, msg)
	logmsg = str(priority) + ' ' + time.strftime('%X %x: ') + msg + '\n'
	fd.write(logmsg)
	fd.flush()
	sys.stderr.write(logmsg)

def cleanup():
	pass
