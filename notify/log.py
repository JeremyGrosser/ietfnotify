# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import logging, time

# Constants
NORMAL = logging.INFO
ERROR = logging.ERROR 

#syslog = logging.SysLogHandler()
#syslog.setLevel(logging.ERROR)
#logging.getLogger('').addHandler(syslog)

def log(priority, msg):
	#logging.log(priority, msg)
	print(str(priority) + ' ' + time.strftime('%X %x: ') + msg)

def cleanup():
	pass
