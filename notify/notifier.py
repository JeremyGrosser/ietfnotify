import _mysql
import smtplib
import re
from email.MIMEText import MIMEText

import config
import util
import message

uuidcache = []

def dummyNotification(subscriber, parsed):
	print 'Dummy: ' + repr(subscriber)

def emailNotification(subscriber, parsed):
	print 'Email: ' + repr(subscriber)
	try:
		msg = '''<html>
<head>
 <title>''' + parsed['tag'][0] + '''</title>
 <style type="text/css">
 table {
 	border-spacing: 0;
	border-collapse: collapse;
 }

 td.field1 { background-color: #D99; }
 td.value1 { background-color: #9D9; }
 td.field2 { background-color: #A66; }
 td.value2 { background-color: #6A6; }

 td {
 	border: 1px;
	border-style: solid;
	border-color: #000;
	padding: 5px;
 }
 </style>
</head>

<body>
<table>'''
		color = 0
		for field in parsed:
			for i in parsed[field]:
				if color:
					color = str(1) 
				else:
					color = str(2) 
				msg += '''<tr>
 <td class="field''' + color + '''">''' + field + '''</td>
 <td class="value''' + color + '''">''' + i + '''</td>
</tr>'''

		msg += '''</table>
</body>
</html>'''

		msg = MIMEText(msg)
		msg = msg.as_string()
		message = 'To: ' + subscriber + '\r\n'
		message += 'From: IETF Notifier <' + config.get('notify-email', 'smtpfrom') + '>\r\n'
		message += 'Subject: ' + parsed['tag'][0] + ' has been updated\r\n'
		message += msg

		smtp = smtplib.SMTP(config.get('notify-email', 'smtphost'), config.getint('notify-email', 'smtpport'))
		smtp.sendmail(config.get('notify-email', 'smtpfrom'), subscriber, message)
		smtp.quit()
	except smtplib.SMTPDataError:
		print 'Error sending email notification: ' + subscriber

def atomNotification(subscriber, parsed):
	print 'Atom: ' + repr(subscriber)
	fd = open(subscriber[0], 'w')
	fd.write('''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
	<title>IETF Notification Feed</title>
	<link href="http://www1.tools.ietf.org/events/atom.xml" rel="self"/>
	<updated>''' + util.makeTimestamp() + '''</updated>
	<author>
		<name>IETF Tools Server</name>
	</author>
	<id>urn:uuid:''' + util.makeUUID() + '''</id>
	''')

	for entry in uuidcache:
		e = open(config.get('archive', 'uuid_dir') + '/' + entry[0], 'r')
		message = ''
		for line in e.readlines():
			message += line
		e.close()
		ent = message.parseMessage(message, 1)
		if 'title' in ent:
			title = ent['title'][0]
		else:
			title = 'No title'
		fd.write('''	<entry>
		<title>''' + title + '''</title>
		<link href="http://www1.tools.ietf.org/ietfnotify/events/''' + entry[0] + '''"/>
		<id>urn:uuid:''' + entry[0] + '''</id>
		<updated>''' + ent['date'][0] + '''</updated>
		<summary>''' + repr(ent) + '''</summary>
	</entry>
''')
	fd.write('</feed>\n')
	fd.close()

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
			if subscription[0] in notifyCallbacks:
				f = notifyCallbacks[subscription[0]]
				f(subscription[1], parsed)
				notified.append(subscription[1])
			else:
				print 'Unknown notification type: ' + repr(subscription)
	db.close()
