#!/usr/bin/python
# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details
import notify.network
import notify.util
import notify.archive
import notify.notifier
import notify.message
import notify.config
import time
import os, sys, getopt

from socket import timeout

# The full module must be loaded first to run init code
import notify.log
from notify.log import DEBUG, ERROR, INFO, log, info, debug

daemon = False
opts, args = getopt.getopt(sys.argv, 'dDv')
for arg in args:
	if arg== 'd':	daemon = True
	if arg== 'D':	notify.log.debugMode = True
	if arg== 'v':
		print '$Id'
		sys.exit(0)

def main():
	# Build a uuid cache for feeds
	notify.archive.buildUUIDCache()

	# Start a new listening socket
	sd = notify.network.startServer()

	# Create a buffer for incoming events
	buffer = []

	inc = int(notify.config.get('general', 'accepttimeout'))
	target = time.time() + inc

	info("Starting up notifcation daemon. Listening on %s:%s." % (notify.config.get('general', 'bindaddr'), notify.config.getint('general', 'bindport')))


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
					notify.notifier.sendNotifications(msg)
					notify.message.updateFilters(msg)
				target += inc
				continue
	
			msg = notify.network.getMessage(afd)
			msg = notify.message.parseMessage(msg, 1)
			retnum, retmsg = notify.message.checkRequired(msg)
			if not retnum:
				if len(buffer) > int(notify.config.get('general', 'eventbuffer')):
					retnum = 1
					retmsg = 'Buffer full'
				else:
					buffer.append(msg)
			if not retnum:
				retnum, retmsg = notify.archive.archiveMessage(msg)
			if not retnum:
				notify.network.sendMessage(afd, 'OK-' + retmsg + '\n')
				msg['event-uuid'] = [retmsg]
			else:
				notify.network.sendMessage(afd, 'ERR-' + retmsg + '\n')
			afd.close()
	except KeyboardInterrupt:
		info('Caught keyboard interrupt, cleaning up.')
		notify.notifier.cleanup()
		sd.close()

# Fork if we're in daemon mode
if daemon:
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
		open(notify.config.get('general', 'pidfile'), 'w').write(str(pid))
		sys.exit(0)
except OSError, e:
	print 'Second fork failed: ' + e.strerror
	sys.exit(1)

main()
