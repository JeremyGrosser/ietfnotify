# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import account

def showLoginMessage():
	print 'You must be logged in to edit your notifier settings.'

def showSubscriptions(db, username):
	subs = account.getSubscriptions(db, username)
	print '<strong>Your subscriptions</strong>'
	print '<table>'
	count = 0

	print ' <tr class="header">\n  <th>Notification</th>\n  <th>Address</th>\n  <th>Pattern</th>\n </tr>\n'
	for sub in subs.fetch_row(0):
		count += 1
		if count % 2:
			print '	<tr class="gray">'
		else:
			print '	<tr class="white">'
		for field in sub[2:]:
                	print '<td>' + field + '</td>'
                print '''<td><a href="?action=modify&id=''' + sub[0] + '''">Modify</a></td>
		<td><a href="?action=remove&id=''' + sub[0] + '''">Remove</a></td>
        </tr>'''

def showAllSubscriptions(db):
	subs = account.getAllSubscriptions(db)
	print '<strong>All subscriptions</strong>'
	print '<table>'
	count = 0

	print ' <tr class="header">\n  <th>Notification</th>\n  <th>Address</th>\n  <th>Pattern</th>\n  <th>Admin</th>\n </tr>\n'
	for sub in subs.fetch_row(0):
		count += 1
		if count % 2:
			print ' <tr class="gray">'
		else:
			print ' <tr class="white">'
		for field in sub[2:]:
			print '<td>' + str(field) + '</td>'
		print '<td><a href="?action=modify&id=' + sub[0] + '">Modify</a></td>'
		print '<td><a href="?action=remove&id=' + sub[0] + '">Remove</a></td>'
		print '</tr>'
	print '</table>'

def showModifyForm(db, recordid):
	action = 'update'
	if recordid == -1:
		eventType = ''
		param = ''
		pattern = ''
		action = 'add'
	else:
		sub = account.getSubscription(db, recordid)
		sub = sub.fetch_row()
		eventType = sub[0][1]
		param = sub[0][2]
		pattern = sub[0][3]
	print '''<form action="" name="modifyForm" method="POST">
	<input type="hidden" name="action" value="''' + action + '''" />'''
	if not recordid == -1:
		print '<input type="hidden" name="id" value="' + str(recordid) + '" />'
	print '''<table>
		<tr>
			<td>Notification type:</td>
			<td><select name="eventType" onChange="disableAddress()">'''
	db.query('SELECT field FROM eventTypes WHERE type="event" AND admin=0')
	res = db.store_result()
	for type in res.fetch_row(0):
		print '<option>' + type[0] + '</option>\n'
	if account.getAdmin(db):
		db.query('SELECT field FROM eventTypes WHERE type="event" AND admin=1')
		res = db.store_result()
		for type in res.fetch_row(0):
			print '<option>' + type[0] + '</option>\n'
	print '</select></td></tr>'
	print '''		<tr>
			<td>Address:</td>
			<td><input type="text" name="param" value="''' + param + '''" /></td>
		</tr>'''
	#db.query('SELECT field FROM types WHERE type="filter" AND admin=0')
	#res = db.store_result()
	#for type in res.fetch_row(0):
	#	print '<tr><td>' + type[0] + '</td><td><input type="text" name="pattern-' + type[0] + '" /></td></tr>\n'
	print '''		<tr>
			<td>Pattern (Regex):</td>
			<td><input type="text" name="pattern" value="''' + pattern + '''" /></td>
		</tr>
		<tr>
			<td colspan="2" align="center"><input type="submit" value="Submit" /></td>
		</tr>
	</table>
	</form>'''
