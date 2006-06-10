import _mysql
import re

import config

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
