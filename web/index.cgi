#!/usr/bin/python
import template, account, edit
import cgi, os

# DEBUGGING ONLY
import cgitb
cgitb.enable()
# DEBUGGING ONLY

form = cgi.FieldStorage()
#subs = account.getSubscriptions(account.getUser())
subs = account.getSubscriptions('synack@csh.rit.edu')

template.header()

if form.getfirst('action') == 'modify' and 'eventType' in form and 'param' in form:
	edit.showModifyForm(form.getfirst('eventType'), form.getfirst('param'))
print '''<table cellspacing="1" cellpadding="2">
	<tr>
		<td><strong>Type</strong></td>
		<td><strong>Target</strong></td>
	</tr>'''
for sub in subs:
	print '''	<tr>
		<td>''' + sub[1] + '''</td>
		<td>''' + sub[2] + '''</td>
		<td><a href="?action=modify&eventType=''' + sub[1] + '''&param=''' + sub[2] + '''">Modify</a></td>
	</tr>'''
template.footer()
