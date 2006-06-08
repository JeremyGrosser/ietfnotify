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
elif form.getfirst('action') == 'modify' and 'id' in form:
	forms.showModifyForm(int(form.getfirst('id')))
elif form.getfirst('action') == 'update' and 'id' in form:
	account.updateSubscription(int(form.getfirst('id')), form.getfirst('eventType'), form.getfirst('param'), form.getfirst('pattern'))
	forms.showSubscriptions(account.getUser())
elif form.getfirst('action') == 'remove' and 'id' in form:
	account.removeSubscription(int(form.getfirst('id')))
	forms.showSubscriptions(account.getUser())
else:
	forms.showSubscriptions(account.getUser())

template.footer()
