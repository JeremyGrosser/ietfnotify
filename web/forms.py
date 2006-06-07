import account

def showLoginMessage():
	print 'You must be logged in to edit your notifier settings.'

def showSubscriptions(username):
	subs = account.getSubscriptions(username)
	print '<strong>Your subscriptions</strong>'
	print '<table border="1" cellspacing="1" cellpadding="2">'
	count = 0
	for sub in subs:
		if count % 2:
			print '	<tr class="gray">'
		else:
			print '	<tr class="white">'
		sub = sub[1:]
		for i in sub:
                	print '<td>' + i + '</td>'
                print '''<td><a href="?action=modify&eventType=''' + sub[1] + '''&param=''' + sub[2] + '''">Modify</a></td>
		<td><a href="?action=remove&eventType=''' + sub[1] + '''&param=''' + sub[2] + '''">Remove</a></td>
        </tr>'''
	count += 1

def showModifyForm(eventType, param, pattern):
	print '''<form action="index.cgi" method="GET">
	<table>
		<tr>
			<td>Event type:</td>
			<td><input type="text" name="eventType" value="''' + eventType + '''" /></td>
		</tr>
		<tr>
			<td>Target:</td>
			<td><input type="text" name="param" value="''' + param + '''" /></td>
		</tr>
		<tr>
			<td>Pattern:</td>
			<td><input type="text" name="pattern" value="''' + pattern + '''" /></td>
		</tr>
		<tr>
			<td colspan="2" align="center"><input type="submit" value="Submit" /></td>
		</tr>
	</table>'''
