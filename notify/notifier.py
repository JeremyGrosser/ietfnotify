# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import _mysql
import smtplib
import re
from email.MIMEText import MIMEText

import sys
import os
import xmpp

import config
import util
import message
import log

uuidcache = []

# Login to jabber
jid = xmpp.protocol.JID(config.get('notify-jabber', 'jid'))
client = xmpp.Client(jid.getDomain(), debug=[])
client.connect()
client.auth(jid.getNode(), config.get('notify-jabber', 'password'))

def cleanup():
	client.disconnect()

def dummyNotification(subscriber, parsed):
	log.log(log.NORMAL, 'Dummy: ' + repr(subscriber))

def jabberNotification(subscriber, parsed):
	log.log(log.NORMAL, 'Jabber: ' + repr(subscriber))
	msg = ''
	for field in parsed:
		for i in parsed[field]:
			msg += field + ' - ' + i + '\n'

	client.send(xmpp.protocol.Message(subscriber, msg))

def emailNotification(subscriber, parsed):
	log.log(log.NORMAL, 'Plain email: ' + repr(subscriber))
	try:
		msg = message.textMessage(parsed, '\r\n')
		msg = MIMEText(msg)
		msg = msg.as_string()
		eml = 'To: ' + subscriber + '\r\n'
		eml += 'From: IETF Notifier <' + config.get('notify-email', 'smtpfrom') + '>\r\n'
		eml += 'Subject: ' + parsed['doc-tag'][0] + ' has been updated\r\n'
		eml += msg

		smtp = smtplib.SMTP(config.get('notify-email', 'smtphost'), config.getint('notify-email', 'smtpport'))
		smtp.sendmail(config.get('notify-email', 'smtpfrom'), subscriber, eml)
		smtp.quit()
	except smtplib.SMTPDataError:
		log.log(log.ERROR, 'Error sending email notification: ' + subscriber)

def htmlEmailNotification(subscriber, parsed):
	log.log(log.NORMAL, 'HTML email: ' + repr(subscriber))
	try:
		msg = message.htmlMessage(parsed)
		msg = MIMEText(msg)
		msg = msg.as_string()
		eml = 'To: ' + subscriber + '\r\n'
		eml += 'From: IETF Notifier <' + config.get('notify-email', 'smtpfrom') + '>\r\n'
		eml += 'Subject: ' + parsed['doc-tag'][0] + ' has been updated\r\n'
		eml += 'Content-type: text/html; charset=utf-8\r\n'
		eml += msg

		smtp = smtplib.SMTP(config.get('notify-email', 'smtphost'), config.getint('notify-email', 'smtpport'))
		smtp.sendmail(config.get('notify-email', 'smtpfrom'), subscriber, eml)
		smtp.quit()
	except smtplib.SMTPDataError:
		log.log(log.ERROR, 'Error sending email notification: ' + subscriber)

def atomNotification(subscriber, parsed):
	log.log(log.NORMAL, 'Atom: ' + repr(subscriber))
	fd = open(subscriber[0], 'w')

	if 'event-uuid' in parsed:
		uuid = parsed['event-uuid'][0]
	else:
		uuid = util.makeUUID()
	if 'event-date' in parsed:
		date = parsed['event-date'][0]
	else:
		date = util.makeTimestamp()

	fd.write('''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
	<title>IETF Notification Feed</title>
	<link href="http://www1.tools.ietf.org/events/atom.xml" rel="self"/>
	<updated>''' + date + '''</updated>
	<author>
		<name>IETF Tools Server</name>
	</author>
	<id>urn:uuid:''' + uuid + '''</id>
	''')

	for entry in uuidcache:
		e = open(config.get('archive', 'uuid_dir') + '/' + entry[0], 'r')
		message = ''
		for line in e.readlines():
			message += line
		e.close()
		ent = message.parseMessage(message, 1)
		if 'event-subject' in ent:
			title = ent['event-subject'][0]
		else:
			title = 'No title'
		fd.write('''	<entry>
		<title>''' + title + '''</title>
		<link href="http://www1.tools.ietf.org/ietfnotify/events/''' + entry[0] + '''"/>
		<id>urn:uuid:''' + entry[0] + '''</id>
		<updated>''' + ent['event-date'][0] + '''</updated>
		<summary>''' + repr(ent) + '''</summary>
	</entry>
''')
	fd.write('</feed>\n')
	fd.close()

notifyCallbacks = {}
notifyCallbacks['plain_email'] = emailNotification
notifyCallbacks['html_email'] = htmlEmailNotification
notifyCallbacks['rss'] = dummyNotification
notifyCallbacks['atom'] = dummyNotification
notifyCallbacks['jabber'] = jabberNotification

def sendNotifications(parsed):
	log.log(log.NORMAL, 'Sending notifications')
	db = _mysql.connect(config.get('notifier', 'mysqlhost'), config.get('notifier', 'mysqluser'), config.get('notifier', 'mysqlpass'), config.get('notifier', 'mysqldb'))
	db.query('SELECT type,target,pattern FROM subscriptions')
	subs = db.store_result()

	notified = []
	for subscription in subs.fetch_row(0):
		regex = re.compile(subscription[2])
		if (regex.search(parsed['doc-tag'][0]) or subscription[2] == '') and not subscription[2] in notified:
			if subscription[0] in notifyCallbacks:
				f = notifyCallbacks[subscription[0]]
				f(subscription[1], parsed)
				notified.append(subscription[1])
			else:
				log.log(log.ERROR, 'Unknown notification type: ' + repr(subscription))
	db.close()
