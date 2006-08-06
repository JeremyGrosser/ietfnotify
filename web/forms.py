# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import account, config, archive
import os, time

def showLoginMessage():
	print 'You must be logged in to edit your notifier settings.'

def showHelp():
	print '''<p><strong>Subscription form</strong>
<br />The notification type sets the method in which you'll be notified. Address sets the address the notification will be sent to. Email notifications can only be sent to the address you're logged in with. The pattern is a <a href="http://www.python.org/doc/current/lib/re-syntax.html">regular expression</a>. An example tag is <em>draft-ietf-tools-draft-info-04</em>. The default action for all fields will not filter at all, meaning that any notification will be passed through.</p>
<p><strong>Your subscriptions</strong>
<br />A list of your current subscriptions is displayed. The fields correspond to the fields on the subscription form. You can modify an existing subscription or remove it using the links to the right.</p>'''

def showSubscriptions(db):
	print '''
<strong>Your subscriptions</strong>
<br />
<table width="100%">
<tr class="header">
 <th class="subs">Notification</th>
 <th class="subs">Address</th>
 <th class="subs">doc-tag filter</th>
 <th class="subs" colspan="4">Actions</th>
</tr>'''
	for sub in account.getSubscriptions(db):
		print '''
<tr class="%(color)s">
 <td class="subs">%(notification)s</td>
 <td class="subs">%(address)s</td>
 <td class="subs">%(filter)s</td>
 <td class="subs"><a href="?action=modify&id=%(id)s">Modify</a></td>
 <td class="subs"><a href="?action=remove&id=%(id)s">Remove</a></td>
 <td class="subs"><a href="?action=duplicate&id=%(id)s">Duplicate</a></td>
 <td class="subs"><a href="?action=%(enableaction)s&id=%(id)s">%(enableaction)s</a></td>
</tr>''' % sub
	print '</table>'

def showAllSubscriptions(db):
	print '''
<strong>All subscriptions</strong>
<br />
<table width="100%">
<tr class="header">
 <th class="subs">Notification</th>
 <th class="subs">Address</th>
 <th class="subs">doc-tag</th>
 <th class="subs" colspan="4">Actions</th>
</tr>'''
	for sub in account.getAllSubscriptions(db):
		print '''
<tr class="%(color)s">
 <td class="subs">%(notification)s</td>
 <td class="subs">%(address)s</td>
 <td class="subs">%(filter)s</td>
 <td class="subs"><a href="?action=modify&id=%(id)s">Modify</a></td>
 <td class="subs"><a href="?action=remove&id=%(id)s">Remove</a></td>
 <td class="subs"><a href="?action=duplicate&id=%(id)s">Duplicate</a></td>
 <td class="subs"><a href="?action=%(enableaction)s&id=%(id)s">%(enableaction)s</a></td>
</tr>''' % sub
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
  <th>Hidden</th>
  <th>Field</th>
 </tr>'''

	db.query('SELECT field,admin FROM eventTypes WHERE type="filter" ORDER BY field')
	res = db.store_result()
	count = 0
	for field in res.fetch_row(0):
		count += 1
		if field[1] == '1':
			checked = 'checked '
		else:
			checked = ''
		if count % 2:
			print '<tr class="white">'
		else:
			print '<tr class="gray">'
		print '<td><input type="checkbox" name="filter-' + field[0] + '" ' + checked + '/></td>'
		print '<td>' + field[0] + '</td>'
	print '<tr><td align="center" colspan="2"><input type="submit" value="Hide" /></td></tr>'
	print '</table>\n</form>'

def showArchived(year, month):
	if month < 1 or month > 12:
		print '<br />Please enter a month between 1 and 12'
		return 0
	if month < 10:
		monthstr = '0' + str(month)
	else:
		monthstr = str(month)

	try:
		events = os.listdir(config.get('archive', 'date_dir') + '/' + str(year) + '/' + monthstr)
		for event in events:
			if event[0] != '.':
				archived = archive.getArchived(event)
				for field in archived:
					for value in archived[field]:
						print '<br />' + field + ': ' + value
				print '<hr />'
	except OSError:
		# Directory does not exist
		print '<br />There are no events archived for the given date'
		return 0

def showArchiveSearch():
	defaults = {}
	t = time.gmtime()
	defaults['currentmonth'] = t[1]
	defaults['currentyear'] = t[0]

	print '''<form action="" method="GET">
<input type="hidden" name="action" value="viewarchive" />
<table>
<tr>
	<td>Month:</td>
	<td><input type="text" name="month" value="%(currentmonth)s" /></td>
</tr>
<tr>
	<td>Year:</td>
	<td><input type="text" name="year" value="%(currentyear)s" /></td>
</tr>
<tr>
	<td colspan="2"><input type="submit" value="Search" /></td>
</tr>
</table>
</form>''' % defaults
