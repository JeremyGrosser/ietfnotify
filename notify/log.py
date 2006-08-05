# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import logging, time, sys, config

# Constants
DEBUG = 'DEBUG'
ERROR = 'ERROR'
INFO = 'INFO'
NETWORK = 'NETWORK'

#syslog = logging.SysLogHandler()
#syslog.setLevel(logging.ERROR)
#logging.getLogger('').addHandler(syslog)

fd = open(config.get('general', 'logfile'), 'a')

def log(priority, msg):
	#logging.log(priority, msg)
	logmsg = str(priority) + ' ' + time.strftime('%x %X: ') + msg + '\n'
	fd.write(logmsg)
	fd.flush()
	if priority != DEBUG:
		sys.stderr.write(logmsg)

def cleanup():
	pass
