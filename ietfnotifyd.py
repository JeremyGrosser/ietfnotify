import notify.network
import notify.util
import notify.archive
import notify.notifier
import notify.message

# Build a uuid cache for feeds
archive.buildUUIDCache()

# Start a new listening socket
sd = notify.network.startServer()

try:
	while 1:
		accepted = sd.accept()
		afd = accepted[0]
		print 'Accepted connection: ' + repr(afd)
		msg = notify.message.parseMessage(notify.network.getMessage(afd), 0)

		retnum, retmsg = notify.message.checkRequired(msg)
		if retnum:
			print 'Message error: ' + retmsg
			notify.network.sendMessage(afd, 'ERR-' + retmsg + '\n')
			afd.close()
		else:
			retnum, retmsg = notify.archive.archiveMessage(msg)
			if retnum:
				print 'Archive error: ' + retmsg
				notify.network.sendMessage(afd, 'ERR-', retmsg + '\n')
			else:
				notify.network.sendMessage(afd, 'OK-' + retmsg + '\n')
			afd.close()
			print 'Sending notifications'
			notify.notifier.sendNotifications(msg)
except KeyboardInterrupt:
	print 'Caught keyboard interrupt, cleaning up.'
	sd.close()
