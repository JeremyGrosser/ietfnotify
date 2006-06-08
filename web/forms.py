import account

def showLoginMessage():
	print 'You must be logged in to edit your notifier settings.'

def showSubscriptions(username):
	subs = account.getSubscriptions(username)
	print '<strong>Your subscriptions</strong>'
	print '<table>'
	for i in range(0, len(subs)):
		subs[i] = subs[i][1:]
		if i % 2:
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
	if len(subs[id]) > 3:
		pattern = subs[id][3]
	else:
		pattern = ''
	print '''<form action="" method="GET">
	<input type="hidden" name="action" value="update" />
	<input type="hidden" name="id" value="''' + str(id) + '''" />
	<table>
		<tr>
			<td>Event type:</td>
			<td><input type="text" name="eventType" value="''' + subs[id][1] + '''" /></td>
		</tr>
		<tr>
			<td>Target:</td>
			<td><input type="text" name="param" value="''' + subs[id][2] + '''" /></td>
		</tr>
		<tr>
			<td>Pattern:</td>
			<td><input type="text" name="pattern" value="''' + pattern + '''" /></td>
		</tr>
		<tr>
			<td colspan="2" align="center"><input type="submit" value="Submit" /></td>
		</tr>
	</table>'''
