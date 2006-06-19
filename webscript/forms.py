# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import account

def showLoginMessage():
	print 'You must be logged in to edit your notifier settings.'

def showHelp():
	print '''<h3>Subscription form</h3>
The notification type sets the method in which you'll be notified. Address sets the address the notification will be sent to. Email notifications can only be sent to the address you're logged in with. The pattern is a <a href="http://www.python.org/doc/current/lib/re-syntax.html">regular expression</a> that is searched on the Tag field of the notification. An example tag is <em>draft-ietf-tools-draft-info-04</em>
<h3>Your subscriptions</h3>
A list of your current subscriptions is displayed. The fields correspond to the fields on the subscription form. You can modify an existing subscription or remove it using the links to the right.'''

def showSubscriptions(db):
	subs = account.getSubscriptions(db)
	print '<strong>Your subscriptions</strong>'
	print '<table>'
	count = 0

	print ' <tr class="header">\n  <th>Notification</th>\n  <th>Address</th>\n  <th>doc-tag filter</th>\n </tr>\n'
	for sub in subs.fetch_row(0):
		count += 1
		if count % 2:
			print '	<tr class="gray">'
		else:
			print '	<tr class="white">'
		for field in sub[2:]:
			print '<td>' + field + '</td>'
		print '<td>' + account.getTagFilter(db, int(sub[0])) + '</td>'
		print '''<td><a href="?action=modify&id=''' + sub[0] + '''">Modify</a></td>
		<td><a href="?action=remove&id=''' + sub[0] + '''">Remove</a></td>
        </tr>'''

def showAllSubscriptions(db):
	subs = account.getAllSubscriptions(db)
	print '<strong>All subscriptions</strong>'
	print '<table>'
	count = 0

	print ' <tr class="header">\n  <th>Notification</th>\n  <th>Address</th>\n  <th>Admin</th>\n  <th>doc-tag</th>\n </tr>\n'
	for sub in subs.fetch_row(0):
		count += 1
		if count % 2:
			print ' <tr class="gray">'
		else:
			print ' <tr class="white">'
		for field in sub[2:]:
			print '<td>' + str(field) + '</td>'
		print '<td>' + account.getTagFilter(db, int(sub[0])) + '</td>'
		print '<td><a href="?action=modify&id=' + sub[0] + '">Modify</a></td>'
		print '<td><a href="?action=remove&id=' + sub[0] + '">Remove</a></td>'
		print '</tr>'
	print '</table>'

def showModifyForm(db, recordid):
	action = 'update'
	if recordid == -1:
		eventType = ''
		param = ''
		action = 'add'
	else:
		sub = account.getSubscription(db, recordid)
		sub = sub.fetch_row()
		eventType = sub[0][1]
		param = sub[0][2]
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
		if type[0] == eventType:
			print '<option selected>' + type[0] + '</option>\n'
		else:
			print '<option>' + type[0] + '</option>\n'
	if account.getAdmin(db):
		db.query('SELECT field FROM eventTypes WHERE type="event" AND admin=1')
		res = db.store_result()
		for type in res.fetch_row(0):
			if type[0] == eventType:
				print '<option selected>' + type[0] + '</option>\n'
			else:
				print '<option>' + type[0] + '</option>\n'
	print '</select></td></tr>'
	print '''		<tr>
			<td>Address:</td>
			<td><input type="text" name="param" value="''' + param + '''" /></td>
		</tr>'''
	res = account.getFilters(db, recordid)
	for field in res:
		print '<tr><td>' + field + '</td><td><input type="text" name="filter-' + field + '" value="' + res[field] + '" /></td></tr>\n'
	print '''		<tr>
		<tr>
			<td colspan="2" align="center"><input type="submit" value="Submit" /></td>
		</tr>
	</table>
	</form>'''

def showFieldsList(db):
	print '''<form action="" method="GET">
<input type="hidden" name="action" value="removefields" />
<table>
 <tr class="header">
  <th>Delete</th>
  <th>Field</th>
 </tr>'''

	db.query('SELECT field FROM eventTypes WHERE type="filter"')
	res = db.store_result()
	count = 0
	for field in res.fetch_row(0):
		count += 1
		if count % 2:
			print '<tr class="white">'
		else:
			print '<tr class="gray">'
		print '<td><input type="checkbox" name="filter-' + field[0] + '" /></td>'
		print '<td>' + field[0] + '</td>'
	print '<tr><td align="center" colspan="2"><input type="submit" value="Delete" /></td></tr>'
	print '</table>\n</form>'
