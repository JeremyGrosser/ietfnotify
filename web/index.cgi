#!/usr/bin/python
import template, account, forms
import cgi, os

# DEBUGGING ONLY
import cgitb
cgitb.enable()
# DEBUGGING ONLY

form = cgi.FieldStorage()

template.header()

done = 0
if account.getUser() == '':
	forms.showLoginMessage()
	done = 1
if form.getfirst('action') == 'modify' and 'id' in form:
	forms.showModifyForm(int(form.getfirst('id')))
	done = 1
if form.getfirst('action') == 'update' and 'id' in form:
	account.updateSubscription(int(form.getfirst('id')), form.getfirst('eventType'), form.getfirst('param'), form.getfirst('pattern'))
if form.getfirst('action') == 'remove' and 'id' in form:
	account.removeSubscription(int(form.getfirst('id')))
if form.getfirst('action') == 'add':
	if 'eventType' in form and 'param' in form:
		account.addSubscription(form.getfirst('eventType'), form.getfirst('param'), form.getfirst('pattern'))
	else:
		forms.showModifyForm(-1)
		done = 1

if not done:
	forms.showSubscriptions(account.getUser())

template.footer()
