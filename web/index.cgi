#!/usr/bin/python
import template, account, forms
import cgi, os

# DEBUGGING ONLY
import cgitb
cgitb.enable()
# DEBUGGING ONLY

form = cgi.FieldStorage()

template.header()

if account.getUser() == '':
	forms.showLoginMessage()

if form.getfirst('action') == 'modify' and 'eventType' in form and 'param' in form:
	if not 'pattern' in form:
		pattern = ''
	else:
		pattern = form.getfirst('pattern')
	forms.showModifyForm(form.getfirst('eventType'), form.getfirst('param'), pattern)
elif not account.getUser() == '':
	forms.showSubscriptions(account.getUser())
	#forms.showSubscriptions('synack@csh.rit.edu')

template.footer()
