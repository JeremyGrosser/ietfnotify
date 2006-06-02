import ConfigParser
import socket
import os
import time

CONFIG_FILE = 'server.conf'
DATA_DIR = '/Users/jeremy/src/ietfnotify/data/'

config = ConfigParser.ConfigParser()
fp = open(CONFIG_FILE, 'r')
config.readfp(fp)
fp.close()

def getMessage(sock):
	msg = ''
	buf = ' ' * 1024
	while len(buf) >= 1024:
		buf = sock.recv(1024)
		msg += buf
	return msg

def parseMessage(msg):
	lines = msg.split('\n')
	parsed = {}
	for line in lines:
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
	checkRequired(parsed)
	archiveMessage(parsed)
	#sendNotifications(parsed)

def archiveMessage(parsed):
	# Generate a new UUID
	uuid = os.popen('uuidgen', 'r').readlines()
	uuid = uuid[0]
	uuid = uuid[:-1]

	os.chdir(DATA_DIR)
	fd = open(uuid, 'w+')
	for key in parsed:
		for i in range(0, len(parsed[key])):
			fd.write(key + ': ' + parsed[key][i] + '\n')
	fd.close()

def checkRequired(parsed):
	tag = parsed['tag'][0].split('-', 1)
	event_type = tag[0]

	if config.has_section('fields-' + event_type):
		items = config.items('fields-' + event_type)
		for i in items:
			if i[0] == 'required':
				required_fields = i[1].split(', ')
				for field in required_fields:
					if not field in parsed:
						return 1
					else:
						pass
						#print 'Required field ' + field + ' received'
			elif i[0] == 'optional':
				optional_fields = i[1].split(', ')
				for field in optional_fields:
					if field in parsed:
						pass
			else:
				print 'Unknown definition in config: ' + repr(i)
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

if config.get('general', 'socktype') == 'inet':
	domain = socket.AF_INET
	bindaddr = config.get('general', 'bindaddr')
else:
	domain = socket.AF_UNIX
	bindaddr = '/tmp/ietf_eventfd'

sd = socket.socket(domain, socket.SOCK_STREAM)
sd.bind(bindaddr)
sd.listen(20)

while 1:
	accepted = sd.accept()
	afd = accepted[0]
	parseMessage(getMessage(afd))

sd.close()
