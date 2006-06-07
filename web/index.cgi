#!/usr/bin/python
import template, account
import cgi, os

# DEBUGGING ONLY
import cgitb
cgitb.enable()
# DEBUGGING ONLY

form = cgi.FieldStorage()
#subs = account.getSubscriptions(account.getUser())
subs = account.getSubscriptions('synack@csh.rit.edu')

template.header()
print '''<table>
	<tr>
		<td><strong>Notification Type</strong></td>
		<td><strong>Parameters</strong></td>
	</tr>'''
for sub in subs:
	print '''	<tr>
		<td>''' + sub[1] + '''</td>
		<td>''' + sub[2] + '''</td>
		<td><a href="modify.cgi?eventType=''' + sub[1] + '''&param=''' + sub[2] + '''">Modify</a></td>
	</tr>'''
template.footer()
