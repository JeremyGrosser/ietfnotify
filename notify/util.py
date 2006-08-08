# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import time
import os

def makeTimestamp():
	return time.strftime('%Y-%m-%dT%H:%M:%S%:z')

def makeUUID():
	uuid = os.popen('uuidgen -t', 'r').readlines()
	uuid = uuid[0]
	return uuid[:-1]
