import account

def showLoginMessage():
	print 'You must be logged in to edit your notifier settings.'

def showSubscriptions(username):
	subs = account.getSubscriptions(username)
	print '<strong>Your subscriptions</strong>'
	print '<table>'
	for i in range(0, len(subs)):
		subs[i] = subs[i][1:]
		if not i % 2:
			print '	<tr class="gray">'
		else:
			print '	<tr class="white">'
		for field in subs[i]:
                	print '<td>' + field + '</td>'
		if len(subs[i]) > 2:
			pattern = '&pattern=' + subs[i][2]
		else:
			pattern = ''
                print '''<td><a href="?action=modify&id=''' + str(i) + '''">Modify</a></td>
		<td><a href="?action=remove&id=''' + str(i) + '''">Remove</a></td>
        </tr>'''

def showModifyForm(id):
	subs = account.getSubscriptions(account.getUser())
	action = 'update'
	if id == -1:
		eventType = ''
		param = ''
		pattern = ''
		action = 'add'
	else:
		eventType = subs[id][1]
		param = subs[id][2]
		pattern = subs[id][3]
	print '''<form action="" method="GET">
	<input type="hidden" name="action" value="''' + action + '''" />'''
	if not id == -1:
		print '<input type="hidden" name="id" value="' + str(id) + '" />'
	print '''<table>
		<tr>
			<td>Notification type:</td>
			<td><select name="eventType" value="''' + eventType + '''"><option>email</option></select></td>
		</tr>
		<tr>
			<td>Address:</td>
			<td><input type="text" name="param" value="''' + param + '''" /></td>
		</tr>
		<tr>
			<td>Pattern (Regex):</td>
			<td><input type="text" name="pattern" value="''' + pattern + '''" /></td>
		</tr>
		<tr>
			<td colspan="2" align="center"><input type="submit" value="Submit" /></td>
		</tr>
	</table>'''
