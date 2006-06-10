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

### REMOVE AFTER MODULARIZATION
CONFIG_FILE = 'server.conf'

config = ConfigParser.ConfigParser()
fp = open(CONFIG_FILE, 'r')
config.readfp(fp)
fp.close()
### REMOVE AFTER MODULARIZATION

notifyCallbacks = {}
uuidcache = []

def parseMessage(msg, keepdate):
	lines = msg.split('\n')
	parsed = {}
	# Make some sense of the data
	for line in lines:
		if line.find(':') == -1:
			break
		line = line.split(':', 1)
		line[0] = line[0].lower()
		line[1] = line[1][1:]
		if line[0] in parsed:
			parsed[line[0]].append(line[1])
		else:
			parsed[line[0]] = [line[1]]
	# Generate a timestamp
	if not keepdate:
		parsed['date'] = [notify.util.makeTimestamp()]
	return parsed

def checkRequired(parsed):
	if not 'tag' in parsed:
		return (1, 'No tag specified')
	tag = parsed['tag'][0].split('-', 1)
	event_type = tag[0]

	# Jump through a few hoops to figure out if we have all of the required
	# fields
	if config.has_section('fields-' + event_type):
		items = config.items('fields-' + event_type)
		for i in items:
			if i[0] == 'required':
				required_fields = i[1].split(', ')
				for field in required_fields:
					if not field in parsed:
						return (1, 'Required field \'' + field + '\' is missing')
			elif i[0] == 'optional':
				return (0, '')
			#	optional_fields = i[1].split(', ')
			#	for field in optional_fields:
			#		if field in parsed:
			#			pass
			else:
				return (1, 'Unknown definition in config: ' + repr(i))
	else:
		print 'Event type not specified in config file. Adding section. All fields will be added as optional. Fix this soon.'
		config.add_section('fields-' + event_type)
		oldkey = ''
		for key in parsed:
			if oldkey == '':
				newkey = key
			else:
				newkey = oldkey + ', ' + key
			config.set('fields-' + event_type, 'optional', newkey)
			oldkey = config.get('fields-' + event_type, 'optional')
		fd = open(CONFIG_FILE, 'w')
		config.write(fd)
		fd.close()
		return (0, '')

# Main method type stuff

# Register notification types
def emailNotification(subscriber, parsed):
	print 'Email: ' + repr(subscriber)
	try:
		msg = ''
		for field in parsed:
			for i in parsed[field]:
				msg += field + ' - ' + i + '\r\n'

		msg = MIMEText(msg)
		msg = msg.as_string()
		message = 'To: ' + subscriber[0] + '\r\n'
		message += 'From: IETF Notifier <' + config.get('notify-email', 'smtpfrom') + '>\r\n'
		message += 'Subject: ' + parsed['tag'][0] + ' has been updated\r\n'
		message += msg

		smtp = smtplib.SMTP(config.get('notify-email', 'smtphost'), config.getint('notify-email', 'smtpport'))
		smtp.sendmail(config.get('notify-email', 'smtpfrom'), subscriber[0], message)
		smtp.quit()
	except smtplib.SMTPDataError:
		print 'Error sending email notitification: ' + subscriber[0]
		print sys.exc_info()[1]

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
		ent = parseMessage(message, 1)
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
notifyCallbacks['email'] = emailNotification
notifyCallbacks['rss'] = rssNotification
notifyCallbacks['atom'] = atomNotification

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
		msg = parseMessage(notify.network.getMessage(afd), 0)

		retnum, retmsg = checkRequired(msg)
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
