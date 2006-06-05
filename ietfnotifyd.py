import ConfigParser
import socket
import os
import time
import smtplib
from email.MIMEText import MIMEText

CONFIG_FILE = 'server.conf'
DATA_DIR = '/home/synack/ietfnotify/data'
UUID_DIR = DATA_DIR + '/uuid'
DATE_DIR = DATA_DIR + '/date'
SUBSCRIPTIONS_FILE = '/home/synack/ietfnotify/subscriptions.csv'
SMTP_HOST = '127.0.0.1'
SMTP_PORT = '25'
SMTP_FROM = 'notifications@tools.ietf.org'

config = ConfigParser.ConfigParser()
fp = open(CONFIG_FILE, 'r')
config.readfp(fp)
fp.close()

notifyCallbacks = {}

def getMessage(sock):
	msg = ''
	buf = ' ' * 1024
	while buf != '\n':
		buf = sock.recv(1024)
		msg += buf
	return msg

def sendMessage(sock, message):
	msglen = len(message)
	while msglen > 0:
		sent = sock.send(message)
		message = message[sent:]
		msglen -= sent

def parseMessage(msg):
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
	timezone = time.timezone / 36
	if timezone < 0:
		timezone += timezone * 2
	else:
		timezone -= timezone * 2
	parsed['date'] = [time.strftime('%Y-%d-%mT%H:%M:%S%z')]

	# Check the event's required fields based on the config file
	if checkRequired(parsed):
		return 1

	# Archive the message
	uuid = archiveMessage(parsed)
	
	# Send notifications to subscribed entities
	sendNotifications(parsed)
	return uuid

def sendNotifications(parsed):
	subsfd = open(SUBSCRIPTIONS_FILE, 'r')
	subs = subsfd.readlines()
	subsfd.close()

	for subscription in subs:
		subscription = subscription[:-1]
		subscription = subscription.split(',')
		if subscription[0] in notifyCallbacks:
			f = notifyCallbacks[subscription[0]]
			f(subscription[1:], parsed)
		else:
			print 'Unknown notification type: ' + repr(subscription)

def archiveMessage(parsed):
	global errmsg
	# Generate a new UUID
	uuid = os.popen('uuidgen', 'r').readlines()
	uuid = uuid[0]
	uuid = uuid[:-1]

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
		errmsg = 'Unable to symlink the same uuid twice!'
		os.remove(UUID_DIR + '/' + uuid)
		return 1
	return uuid

def checkRequired(parsed):
	global errmsg
	if not 'tag' in parsed:
		return 1
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
						errmsg = 'Required field \'' + field + '\' is missing'
						return 1
			elif i[0] == 'optional':
				pass
			#	optional_fields = i[1].split(', ')
			#	for field in optional_fields:
			#		if field in parsed:
			#			pass
			else:
				errmsg = 'Unknown definition in config: ' + repr(i)
				return 1
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
		return 0


# Main method type stuff
if config.get('general', 'socktype') == 'inet':
	domain = socket.AF_INET
	bindaddr = (config.get('general', 'bindaddr'), config.getint('general', 'bindport'))
else:
	domain = socket.AF_UNIX
	bindaddr = '/tmp/ietf_eventfd'

# Register notification types
def emailNotification(subscriber, parsed):
	try:
		print 'Sending notification: ' + subscriber[0]
		msg = ''
		for field in parsed:
			for i in parsed[field]:
				msg += field + ' - ' + i + '\n'

		msg = MIMEText(msg)
		msg = msg.as_string()
		message = 'To: ' + subscriber[0] + '\n'
		message += 'From: ' + SMTP_FROM + '\n'
		message += msg
		print 'Sending -> ' + message

		smtp = smtplib.SMTP(SMTP_HOST)
		smtp.sendmail(SMTP_FROM, subscriber[0], message)
		smtp.quit()
	except smtplib.SMTPDataError:
		print 'Error sending email notitification: ' + subscriber[0]
def rssNotification(subscriber, parsed):
	print 'RSS: ' + repr(subscriber)
def atomNotification(subscriber, parsed):
	print 'Atom: ' + repr(subscriber)
notifyCallbacks['email'] = emailNotification
notifyCallbacks['rss'] = rssNotification
notifyCallbacks['atom'] = atomNotification

sd = socket.socket(domain, socket.SOCK_STREAM)
sd.bind(bindaddr)
sd.listen(20)

try:
	while 1:
		accepted = sd.accept()
		afd = accepted[0]
		ret = parseMessage(getMessage(afd))
		if ret == 1:
			sendMessage(afd, 'ERR-' + errmsg + '\n')
			afd.close()
		else:
			sendMessage(afd, 'OK-' + ret + '\n')
			afd.close()
except KeyboardInterrupt:
	print 'Caught keyboard interrupt, cleaning up.'
	sd.close()
