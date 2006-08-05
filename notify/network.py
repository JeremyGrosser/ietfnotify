# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import socket
import config
import log

def getMessage(sock):
	log.log(log.DEBUG, 'Receiving message from socket')
	msg = ''
	buf = ''
	while buf != 0:
		buf = sock.recv(config.getint('general', 'recvbuffer'))
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

def startServer():
	log.log(log.DEBUG, 'Starting listening server')
	if config.get('general', 'socktype') == 'inet':
		domain = socket.AF_INET
		bindaddr = (config.get('general', 'bindaddr'), config.getint('general', 'bindport'))
	else:
		domain = socket.AF_UNIX
		bindaddr = config.get('general', 'bindaddr')
	
	sd = socket.socket(domain, socket.SOCK_STREAM)
	sd.bind(bindaddr)
	sd.listen(20)
	sd.settimeout(float(config.get('general', 'accepttimeout')))
	return sd
