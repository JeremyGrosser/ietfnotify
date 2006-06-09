import ConfigParser
import socket
import os
import time
import smtplib
import sys
import re
import _mysql
from email.MIMEText import MIMEText

CONFIG_FILE = 'server.conf'
DATA_DIR = '/home/synack/ietfnotify/data'
UUID_DIR = DATA_DIR + '/uuid'
DATE_DIR = DATA_DIR + '/date'

config = ConfigParser.ConfigParser()
fp = open(CONFIG_FILE, 'r')
config.readfp(fp)
fp.close()

notifyCallbacks = {}
uuidcache = []

def getMessage(sock):
	msg = ''
	buf = ''
	while buf != 0:
		buf = sock.recv(1024)
		msg += buf
		if msg[-2:] == '\n\n':
			return msg
	return msg

def sendMessage(sock, message):
	msglen = len(message)
	while msglen > 0:
		sent = sock.send(message)
		message = message[sent:]
		msglen -= sent

def makeTimestamp():
	tz = time.strftime('%z')
	tz = '-' + tz[1:]
	tz = tz[:3] + ':' + tz[3:]
	return time.strftime('%Y-%d-%mT%H:%M:%S') + tz

def makeUUID():
        uuid = os.popen('uuidgen -t', 'r').readlines()
	uuid = uuid[0]
	return uuid[:-1]

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
		parsed['date'] = [makeTimestamp()]
	return parsed

def sendNotifications(parsed):
	db = _mysql.connect('localhost', 'synack', 'rtz2096', 'ietfnotify')
	db.query('SELECT type,target,pattern FROM subscriptions')
	subs = db.store_result()
	print 'Sending notification: ' + repr(parsed)

	notified = []
	for subscription in subs.fetch_row(maxrows=0):
		if not subscription[2] in notified:
			if not subscription[2] == '':
				regex = re.compile(subscription[2])
				if not regex.match(parsed['tag'][0]):
					break
			if subscription[0] in notifyCallbacks:
				f = notifyCallbacks[subscription[0]]
				f(subscription[1:], parsed)
				notified.append(subscription[2])
			else:
				print 'Unknown notification type: ' + repr(subscription)
	db.close()

def archiveMessage(parsed):
	# Generate a new UUID
	uuid = makeUUID()

	# Write the event to a file named with the UUID
	os.chdir(UUID_DIR)
	fd = open(uuid, 'w+')
	for key in parsed:
		for i in range(0, len(parsed[key])):
			fd.write(key + ': ' + parsed[key][i] + '\n')
	fd.close()

	year = parsed['date'][0][:4]
	month = parsed['date'][0][8:10]
	symlink_source = UUID_DIR + '/' + uuid
	symlink_dest = DATE_DIR + '/' + year + '/' + month + '/' + uuid
	try:
		os.makedirs(DATE_DIR + '/' + year + '/' + month)
	except OSError: pass

	try:
		os.symlink(symlink_source, symlink_dest)
	except OSError:
		os.remove(UUID_DIR + '/' + uuid)
		return (1, 'Unable to symlink the same uuid twice!')

	# Update the uuid cache
	uuidcache.insert(0, (uuid, 0))
	return (0, uuid)

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
				pass
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
if config.get('general', 'socktype') == 'inet':
	domain = socket.AF_INET
	bindaddr = (config.get('general', 'bindaddr'), config.getint('general', 'bindport'))
else:
	domain = socket.AF_UNIX
	bindaddr = '/tmp/ietf_eventfd'

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
		message += 'From: IETF Notifier <' + config.get('general', 'smtpfrom') + '>\r\n'
		message += 'Subject: ' + parsed['tag'][0] + ' has been updated\r\n'
		message += msg

		smtp = smtplib.SMTP(config.get('general', 'smtphost'), config.getint('general', 'smtpport'))
		smtp.sendmail(config.get('general', 'smtpfrom'), subscriber[0], message)
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
	<updated>""" + makeTimestamp() + """</updated>
	<author>
		<name>IETF Tools Server</name>
	</author>
	<id>urn:uuid:""" + makeUUID() + """</id>
	""")

	for entry in uuidcache:
		e = open(UUID_DIR + '/' + entry[0], 'r')
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
listing = os.listdir(UUID_DIR)
for file in listing:
	st = os.stat(UUID_DIR + '/' + file)
	uuidcache.append( (file, st[9]) ) # ctime
uuidcache.sort()
uuidcache = uuidcache[:config.getint('notify-atom', 'feedlength')]

sd = socket.socket(domain, socket.SOCK_STREAM)
sd.bind(bindaddr)
sd.listen(20)

try:
	while 1:
		accepted = sd.accept()
		afd = accepted[0]
		print 'Accepted connection: ' + repr(afd)
		msg = parseMessage(getMessage(afd), 0)

		err = checkRequired(msg)
		if err[0]:
			print 'Message error: ' + err[1]
			sendMessage(afd, 'ERR-' + err[1] + '\n')
			afd.close()
		else:
			err = archiveMessage(msg)
			if err[0]:
				print 'Archive error: ' + err[1]
				sendMessage(afd, 'ERR-', err[1] + '\n')
			else:
				sendMessage(afd, 'OK-' + err[1] + '\n')
			afd.close()
			print 'Sending notifications'
			sendNotifications(msg)
except KeyboardInterrupt:
	print 'Caught keyboard interrupt, cleaning up.'
	sd.close()
