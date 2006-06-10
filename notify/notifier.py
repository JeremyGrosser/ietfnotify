import _mysql
import smtplib
import re
from email.MIMEText import MIMEText

import config

def dummyNotification(subscriber, parsed):
	print 'Dummy: ' + repr(subscriber)

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
		message += 'From: IETF Notifier <' + config.get('notify-email', 'smtpfrom') + '>\r\n'
		message += 'Subject: ' + parsed['tag'][0] + ' has been updated\r\n'
		message += msg

		smtp = smtplib.SMTP(config.get('notify-email', 'smtphost'), config.getint('notify-email', 'smtpport'))
		smtp.sendmail(config.get('notify-email', 'smtpfrom'), subscriber[0], message)
		smtp.quit()
	except smtplib.SMTPDataError:
		print 'Error sending email notification: ' + subscriber[0]

notifyCallbacks = {}
notifyCallbacks['email'] = emailNotification
notifyCallbacks['rss'] = dummyNotification
notifyCallbacks['atom'] = dummyNotification
notifyCallbacks['jabber'] = dummyNotification

def sendNotifications(parsed):
	db = _mysql.connect(config.get('notifier', 'mysqlhost'), config.get('notifier', 'mysqluser'), config.get('notifier', 'mysqlpass'), config.get('notifier', 'mysqldb'))
	db.query('SELECT type,target,pattern FROM subscriptions')
	subs = db.store_result()

	
	notified = []
	for subscription in subs.fetch_row(0):
		regex = re.compile(subscription[2])
		if (regex.match(parsed['tag'][0]) or subscription[2] == '') and not subscription[2] in notified:
			print 'Notifying: ' + repr(subscription)
			if subscription[0] in notifyCallbacks:
				f = notifyCallbacks[subscription[0]]
				f(subscription[1:], parsed)
				notified.append(subscription[2])
			else:
				print 'Unknown notification type: ' + repr(subscription)
	db.close()
