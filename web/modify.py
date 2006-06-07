def showModifyForm(eventType, param):
	print '''<form action="modify.cgi" method="GET">
	<table>
		<tr>
			<td>Event type:</td>
			<td><select name="eventType" value="''' + eventType + '''>
				<option>email</option>
			</select></td>
		</tr>
		<tr>
			<td>Arguments:</td>
			<td><input type="text" name="param" value="''' + param + '''" /></td>
		</tr>
	</table>'''
