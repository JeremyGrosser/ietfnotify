# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
import sys

# Set to zero for normal operation
DEBUGGING = 1

# Constants
NORMAL = 'NORMAL'
ERROR = 'ERROR'

def log(priority, msg):
	if DEBUGGING:
		sys.stderr.write(priority + ': ' + msg + '\n')

	if priority == NORMAL: pass
	if priority == ERROR: pass
