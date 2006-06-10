import ConfigParser
import os
import time
import smtplib
import sys
import re
import _mysql
from email.MIMEText import MIMEText

import notify.network
import notify.util
import notify.archive
import notify.notifier
import notify.message

### REMOVE AFTER MODULARIZATION
CONFIG_FILE = 'server.conf'

config = ConfigParser.ConfigParser()
fp = open(CONFIG_FILE, 'r')
config.readfp(fp)
fp.close()
### REMOVE AFTER MODULARIZATION

notifyCallbacks = {}
uuidcache = []

# Main method type stuff

def rssNotification(subscriber, parsed):
	print 'RSS: ' + repr(subscriber)
def atomNotification(subscriber, parsed):
	print 'Atom: ' + repr(subscriber)
	fd = open(subscriber[0], 'w')
	fd.write("""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<feed xmlns=\"http://www.w3.org/2005/Atom\">
	<title>IETF Notification Feed</title>
	<link href=\"http://shiraz.tools.ietf.org/events/atom.xml\" rel="self"/>
	<updated>""" + notify.util.makeTimestamp() + """</updated>
	<author>
		<name>IETF Tools Server</name>
	</author>
	<id>urn:uuid:""" + notify.util.makeUUID() + """</id>
	""")

	for entry in uuidcache:
		e = open(config.get('archive', 'uuid_dir') + '/' + entry[0], 'r')
		message = ''
		for line in e.readlines():
			message += line
		e.close()
		ent = notify.message.parseMessage(message, 1)
		if 'title' in ent:
			title = ent['title'][0]
		else:
			title = 'No title'
		fd.write("""	<entry>
		<title>""" + title + """</title>
		<link href=\"http://tools.ietf.org/ietfnotify/events/""" + entry[0] + """\"/>
		<id>urn:uuid:""" + entry[0] + """</id>
		<updated>""" + ent['date'][0] + """</updated>
		<summary>""" + repr(ent) + """</summary>
	</entry>
""")
	fd.write('</feed>\n')
	fd.close()

# Build a uuid cache for feeds
listing = os.listdir(config.get('archive', 'uuid_dir'))
for file in listing:
	st = os.stat(config.get('archive', 'uuid_dir') + '/' + file)
	uuidcache.append( (file, st[9]) ) # ctime
uuidcache.sort()
uuidcache = uuidcache[:config.getint('notify-atom', 'feedlength')]

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
