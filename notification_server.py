import ConfigParser
import socket

config = ConfigParser.ConfigParser()
fp = open('server.conf', 'r')
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
	checkRequired(parsed)

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
						print 'Required field ' + i[0] + ' is missing'
			elif i[0] == 'optional':
				optional_fields = i[1].split(', ')
				for field in optional_fields:
					if not field in parsed:
						print 'Optional field ' + i[0] + ' received'
			else:
				print 'Unknown definition in config: ' + repr(i)
	else:
		print 'Unknown event type, not found in config file'

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
