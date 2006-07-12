# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import sys, time
import config

# Set to zero for normal operation
DEBUGGING = 1

# Constants
NORMAL = 'NORMAL'
ERROR = 'ERROR'

logfd = open(config.get('general', 'debuglog'), 'w')

def log(priority, msg):
	if DEBUGGING:
		sys.stderr.write(priority + ': ' + msg + '\n')
		logfd.write(time.strftime('%X %x ') + priority + ': ' + msg + '\n')
		logfd.flush()

	if priority == NORMAL: pass
	if priority == ERROR: pass

def cleanup():
	logfd.close()
