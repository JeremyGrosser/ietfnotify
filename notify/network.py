import socket
import myconfig

def getMessage(sock):
	msg = ''
	buf = ''
	while buf != 0:
		buf = sock.recv(myconfig.getint('general', 'recvbuffer'))
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
	if myconfig.get('general', 'socktype') == 'inet':
		domain = socket.AF_INET
		bindaddr = (myconfig.get('general', 'bindaddr'), config.getint('general', 'bindport'))
	else:
		domain = socket.AF_UNIX
		bindaddr = myconfig.get('general', 'bindaddr')
	
	sd = socket.socket(domain, socket.SOCK_STREAM)
	sd.bind(bindaddr)
	sd.listen(20)
	return sd
