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
	</table>'''
