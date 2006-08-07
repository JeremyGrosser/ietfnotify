# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

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
	log.cleanup()

def dummyNotification(subscriber, parsed):
	log.log(log.DEBUG, 'Dummy: ' + repr(subscriber))

def jabberNotification(subscriber, parsed):
	log.log(log.DEBUG, 'Jabber: ' + repr(subscriber))
	msg = ''
	for field in parsed:
		for i in parsed[field]:
			msg += field + ' - ' + i + '\n'

	client.send(xmpp.protocol.Message(subscriber, msg))

def emailNotification(subscriber, parsed):
	log.log(log.DEBUG, 'Plain email: ' + repr(subscriber))
	try:
		msg = message.renderMessage('email.txt', parsed)
		msg = MIMEText(msg)
		msg = msg.as_string()
		eml = 'To: ' + subscriber + '\r\n'
		eml += 'From: IETF Notifier <' + config.get('notify-email', 'smtpfrom') + '>\r\n'
		eml += 'Subject: ' + parsed['doc-tag'][0] + ' has been updated\r\n'
		eml += 'Precedence: list\r\n'
		eml += 'Auto-submitted: auto-generated\r\n'
		eml += msg

		smtp = smtplib.SMTP(config.get('notify-email', 'smtphost'), config.getint('notify-email', 'smtpport'))
		smtp.sendmail(config.get('notify-email', 'smtpfrom'), subscriber, eml)
		smtp.quit()
	except smtplib.SMTPDataError:
		log.log(log.ERROR, 'Error sending email notification: ' + subscriber)

def htmlEmailNotification(subscriber, parsed):
	log.log(log.DEBUG, 'HTML email: ' + repr(subscriber))
	try:
		msg = message.renderMessage('email.html', parsed)
		msg = MIMEText(msg)
		msg = msg.as_string()
		eml = 'To: ' + subscriber + '\r\n'
		eml += 'From: IETF Notifier <' + config.get('notify-email', 'smtpfrom') + '>\r\n'
		eml += 'Subject: ' + parsed['doc-tag'][0] + ' has been updated\r\n'
		eml += 'Precedence: list\r\n'
		eml += 'Auto-submitted: auto-generated\r\n'
		eml += 'Content-type: text/html; charset=utf-8\r\n'
		eml += msg

		smtp = smtplib.SMTP(config.get('notify-email', 'smtphost'), config.getint('notify-email', 'smtpport'))
		smtp.sendmail(config.get('notify-email', 'smtpfrom'), subscriber, eml)
		smtp.quit()
	except smtplib.SMTPDataError:
		log.log(log.ERROR, 'Error sending email notification: ' + subscriber)

def atomNotification(subscriber, parsed):
	log.log(log.DEBUG, 'Atom: ' + repr(subscriber))

	# Create a pure uuid list without dates
	uuidList = []
	for uuid in uuidcache:
		uuidList.append(uuid[0])

	try:
		fd = open(subscriber, 'w')
		fd.write(message.renderList('atom.xml', uuidList))
		fd.close()
	except IOError:
		log.log(log.ERROR, 'Error writing atom feed')

def rssNotification(subscriber, parsed):
	log.log(log.DEBUG, 'RSS: ' + repr(subscriber))

	uuidList = []
	for uuid in uuidcache:
		uuidList.append(uuid[0])

	try:
		fd = open(subscriber, 'w')
		fd.write(message.renderList('rss.xml', uuidList))
		fd.close()
	except IOError:
		log.log(log.ERROR, 'Error writing rss feed')

notifyCallbacks = {}
notifyCallbacks['plain_email'] = emailNotification
notifyCallbacks['html_email'] = htmlEmailNotification
notifyCallbacks['rss'] = rssNotification
notifyCallbacks['atom'] = atomNotification
notifyCallbacks['jabber'] = jabberNotification

def sendNotifications(parsed):
	db = _mysql.connect(config.get('notifier', 'mysqlhost'), config.get('notifier', 'mysqluser'), config.get('notifier', 'mysqlpass'), config.get('notifier', 'mysqldb'))
	db.query('SELECT type,target,id FROM subscriptions WHERE enabled=1')
	subs = db.store_result()

	parsed = message.removeHidden(db, parsed)

	notified = []
	for subscription in subs.fetch_row(0):
		db.query('SELECT field,pattern FROM filters WHERE parent_id=' + str(subscription[2]))
		filter_res = db.store_result()
		filtered = 0
		for filter in filter_res.fetch_row(0):
			regex = re.compile(filter[1])
			if filter[0] in parsed:
				if regex.search(parsed[filter[0]][0]):
					filtered = 1
			else:
				if regex.search(''):
					filtered = 1

		if not subscription[2] in notified and not filtered:
			if subscription[0] in notifyCallbacks:
				f = notifyCallbacks[subscription[0]]
				f(subscription[1], parsed)
				notified.append(subscription[2])
			else:
				log.log(log.ERROR, 'Unknown notification type: ' + repr(subscription))
	db.close()
