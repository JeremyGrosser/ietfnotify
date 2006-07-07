# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
import sys
import time

# Set to zero for normal operation
DEBUGGING = 1

# Constants
NORMAL = 'NORMAL'
ERROR = 'ERROR'

logfd = open('/home/jeremy/src/ietfnotify/debug.log', 'w')

def log(priority, msg):
	if DEBUGGING:
		sys.stderr.write(priority + ': ' + msg + '\n')
		logfd.write(time.strftime('%X %x ') + priority + ': ' + msg + '\n')
		logfd.flush()

	if priority == NORMAL: pass
	if priority == ERROR: pass

def cleanup():
	logfd.close()
