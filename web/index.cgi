#!/usr/bin/python
import template, account, forms
import cgi, os

# DEBUGGING ONLY
import cgitb
cgitb.enable()
# DEBUGGING ONLY

form = cgi.FieldStorage()

template.header()

if form.getfirst('action') == 'modify' and 'eventType' in form and 'param' in form:
	forms.showModifyForm(form.getfirst('eventType'), form.getfirst('param'))
else:
	#forms.showSubscriptions(account.getUser())
	forms.showSubscriptions('synack@csh.rit.edu')
template.footer()
