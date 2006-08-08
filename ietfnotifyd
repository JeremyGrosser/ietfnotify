#!/usr/bin/env python
# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details
import ietfnotify.network
import ietfnotify.util
import ietfnotify.archive
import ietfnotify.notifier
import ietfnotify.message
import ietfnotify.config
import time
import os, sys, getopt

from socket import timeout

# The full module must be loaded first to run init code
import ietfnotify.log
from ietfnotify.log import DEBUG, ERROR, INFO, log, info, debug

daemon = True
opts, args = getopt.getopt(sys.argv, 'dDv')
for arg in args:
	if arg == '-d':	daemon = False
	if arg == '-D':	ietfnotify.log.debugMode = True
	if arg == '-v':
		print 'ietfnotifyd v0.01 ($Id$)'
		sys.exit(0)

def main():
	# Build a uuid cache for feeds
	ietfnotify.archive.buildUUIDCache()

	# Start a new listening socket
	sd = ietfnotify.network.startServer()

	# Create a buffer for incoming events
	buffer = []

	inc = int(ietfnotify.config.get('general', 'accepttimeout'))
	target = time.time() + inc

	info("Starting up notifcation daemon. Listening on %s:%s." % (ietfnotify.config.get('general', 'bindaddr'), ietfnotify.config.getint('general', 'bindport')))


	try:
		while True:
			newtimeout = max( target - time.time(), 0.1)
			sd.settimeout(newtimeout)
			debug('timeout(' + str(newtimeout) + ')\tbuffer(' + str(len(buffer)) + ')')
	
			try:
				afd, address = sd.accept()
			except timeout:
				debug('target(' + str(target) + ')\ttime.now(' + str(time.time()) + ')')
				if len(buffer) > 0:
					msg = buffer.pop()
					ietfnotify.notifier.sendNotifications(msg)
					ietfnotify.message.updateFilters(msg)
				target += inc
				continue
	
			msg = ietfnotify.network.getMessage(afd)
			msg = ietfnotify.message.parseMessage(msg, 1)
			retnum, retmsg = ietfnotify.message.checkRequired(msg)
			if not retnum:
				if len(buffer) > int(ietfnotify.config.get('general', 'eventbuffer')):
					retnum = 1
					retmsg = 'Buffer full'
				else:
					buffer.append(msg)
			if not retnum:
				retnum, retmsg = ietfnotify.archive.archiveMessage(msg)
			if not retnum:
				ietfnotify.network.sendMessage(afd, 'OK-' + retmsg + '\n')
				msg['event-uuid'] = [retmsg]
			else:
				ietfnotify.network.sendMessage(afd, 'ERR-' + retmsg + '\n')
			afd.close()
	except KeyboardInterrupt:
		info('Caught keyboard interrupt, cleaning up.')
		ietfnotify.notifier.cleanup()
		sd.close()

# Fork if we're in daemon mode
if daemon:
	sys.stdout = sys.stderr = ietfnotify.log.LogStream(open(ietfnotify.config.get('general', 'logfile'), 'a+'))
	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError, e:
		print 'First fork failed: ' + e.strerror
		sys.exit(1)
		os.chdir('/')
		os.setsid()

	try:
		pid = os.fork()
		if pid > 0:
			debug('Forked to PID ' + str(pid))
			open(ietfnotify.config.get('general', 'pidfile'), 'w').write(str(pid))
			sys.exit(0)
	except OSError, e:
		print 'Second fork failed: ' + e.strerror
		sys.exit(1)

main()
