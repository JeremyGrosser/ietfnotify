# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
import sys

# Set to zero for normal operation
DEBUGGING = 1

# Constants
NORMAL = 0
ERROR = 10

def log(priority, msg):
	if DEBUGGING:
		sys.stderr.write(str(priority) + ': ' + msg)

	if priority == NORMAL: pass
	if priority == ERROR: pass
	if priority == CRITICAL: pass
	if priority == FATAL: pass
