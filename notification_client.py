import socket

#msg = """Tag: draft-ietf-tools-document-tags-00
#Date: 2006-07-05T00:00:00:-00:00
#Source: internet-drafts
#Source: id-announce
#Author: H. Levkowetz
#Title: Unique IETF Document and Information Tags
#URL: http://www.leoh.org/ietf/draft/tools/document-tags/draft-ietf-tools-document-tags-00.a.txt
#Pages: 9"""

msg = """Tag: event-ietf-tools-meetup-00
Date: 2006-07-05T00:00:00-00:00
Source: internet-drafts
Source: id-announce
Source: other
Author: J. Grosser
Title: IETF Tools Meetup Event
URL: http://www.example.org/"""

sd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sd.connect('/tmp/ietf_eventfd')
print "Sending message: ", msg
sd.send(msg)
sd.close()
