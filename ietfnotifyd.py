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

from socket import timeout

# The full module must be loaded first to run init code
import notify.log
from notify.log import DEBUG, ERROR, INFO, log

# Build a uuid cache for feeds
notify.archive.buildUUIDCache()

# Start a new listening socket
sd = notify.network.startServer()

# Create a buffer for incoming events
buffer = []

looping = 1
lastpop = 0.0
nextpop = float(notify.config.get('general', 'accepttimeout'))
lastuuid = ''
while looping:
	try:
		log(INFO, 'timeout(' + str(nextpop - lastpop) + ')\tbuffer(' + str(len(buffer)) + ')\tlastuuid(' + lastuuid + ')')
		# Block on accepting a connection... The timeout is set by accepttimeout
		# in the general section of the config file.
		accepted = sd.accept()
		afd = accepted[0]

		# Reset the socket timeout
		sd.settimeout(nextpop - lastpop)
		log(DEBUG, 'Setting timeout to ' + str(nextpop - lastpop))

		# Get the data from the socket and make some sense of it
		msg = notify.message.parseMessage(notify.network.getMessage(afd), 0)

		# Make sure the buffer isn't full
		if len(buffer) < int(notify.config.get('general', 'eventbuffer')):
			# Check the validity of the event
			retnum, retmsg = notify.message.checkRequired(msg)
			if retnum:
				log(ERROR, 'Error checking required fields: ' + retmsg + '\n')
				notify.network.sendMessage(afd, 'ERR-' + retmsg + '\n')
			else:
				# Archive the event
				retnum, retmsg = notify.archive.archiveMessage(msg)
				if retnum:
					notify.network.sendMessage(afd, 'ERR-', retmsg + '\n')
				else:
					msg['event-uuid'] = [retmsg]
					notify.network.sendMessage(afd, 'OK-' + retmsg + '\n')
					buffer.append(msg)
					log(DEBUG, 'Message received with UUID ' + msg['event-uuid'][0])
					lastuuid = msg['event-uuid']
		else:
			# The buffer is full. Log it, tell the socket, and do nothing
			log(ERROR, 'Event buffer is full, lost an event')
			notify.network.sendMessage(afd, 'ERR-Event buffer is full, not processing event\n')
		if (nextpop - time.clock()) < 0:
			raise timeout
		else:
			if len(buffer) > 0:
				sd.settimeout(nextpop - time.clock())
				log(DEBUG, 'Setting timeout to ' + str(nextpop - time.clock()))
			else:
				sd.settimeout(None)
				log(DEBUG, 'Event buffer is empty, disabling timeout.')
		afd.close()
	except KeyboardInterrupt:
		print 'Caught keyboard interrupt, cleaning up.'
		notify.notifier.cleanup()
		sd.close()
		looping = 0
	except timeout:
		if len(buffer) > 0:
			msg = buffer.pop()
			log(DEBUG, 'Buffer size: ' + str(len(buffer)))
			notify.notifier.sendNotifications(msg)
			notify.message.updateFilters(msg)

		nextpop = time.clock() + float(notify.config.get('general', 'accepttimeout'))
