# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import time
import os

def makeTimestamp():
	tz = time.strftime('%z')
	tz = '-' + tz[1:]
	tz = tz[:3] + ':' + tz[3:]
	return time.strftime('%Y-%d-%mT%H:%M:%S') + tz

def makeUUID():
	uuid = os.popen('uuidgen -t', 'r').readlines()
	uuid = uuid[0]
	return uuid[:-1]
