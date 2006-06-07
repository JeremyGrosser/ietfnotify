import account

def showLoginMessage():
	print 'You must be logged in to edit your notifier settings.'

def showSubscriptions(username):
	subs = account.getSubscriptions(username)
	print '''<table cellspacing="1" cellpadding="2">
        <tr>
                <td><strong>Type</strong></td>
                <td><strong>Target</strong></td>
        </tr>'''
	for sub in subs:
		print '''       <tr>
                <td>''' + sub[1] + '''</td>
                <td>''' + sub[2] + '''</td>
                <td><a href="?action=modify&eventType=''' + sub[1] + '''&param=''' + sub[2] + '''">Modify</a></td>
        </tr>'''

def showModifyForm(eventType, param):
	print '''<form action="index.cgi" method="GET">
	<table>
		<tr>
			<td>Event type:</td>
			<td><input type="text" name="eventType" value="''' + eventType + '''" /></td>
		</tr>
		<tr>
			<td>Arguments:</td>
			<td><input type="text" name="param" value="''' + param + '''" /></td>
		</tr>
		<tr>
			<td colspan="2" align="center"><input type="submit" value="Submit" /></td>
		</tr>
	</table>'''
