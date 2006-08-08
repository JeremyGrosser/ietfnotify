#ietfnotify - Receives, archives, and sends notifications related to IETF
#             events, drafts, working groups, etc.
#			 Copyright (C) 2006 Jeremy Grosser

# This script implements an example of a program that connects to ietfnotifyd using a domain
# socket
import socket

# An example notification. Don't forget the two newline characters at the end, they tell the
# daemon to start processing the notification
msg = """Doc-Tag: event-ietf-tools-meetup-00
Event-Source: internet-drafts
Event-Source: id-announce
Event-Source: other
Doc-Title: IETF Tools Meetup Event
Doc-URL: http://www.example.org/\n\n"""

# Create and connect to a domain socket
sd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sd.connect('/tmp/ietf_eventfd')

# Send the notification
print "Sending message:\n", msg
sd.send(msg)
print '> ' + sd.recv(1024)
