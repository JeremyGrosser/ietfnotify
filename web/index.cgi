#!/usr/bin/python
# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import sys
sys.path.insert(0, '/home/synack/ietfnotify/webscript')

import template, account, forms
import cgi, os, _mysql

# DEBUG
import cgitb
cgitb.enable()
# DEBUG

form = cgi.FieldStorage()
db = _mysql.connect('localhost', 'synack', 'rtz2096', 'ietfnotify')

template.header(db)

done = 0
if account.getUser() == '':
	forms.showLoginMessage()
	done = 1
if form.getfirst('action') == 'modify' and 'id' in form:
	forms.showModifyForm(db, int(form.getfirst('id')))
	done = 1
if form.getfirst('action') == 'update' and 'id' in form:
	filters = {} 
	for field in form:
		if field.startswith('filter-'):
			filters[field[7:]] = form.getfirst(field)

	if form.getfirst('eventType') == 'html_email' or form.getfirst('eventType') == 'plain_email':
		account.updateSubscription(db, int(form.getfirst('id')), form.getfirst('eventType'), account.getUser(), filters)
	else:
		account.updateSubscription(db, int(form.getfirst('id')), form.getfirst('eventType'), form.getfirst('param'), filters)
if form.getfirst('action') == 'remove' and 'id' in form:
	account.removeSubscription(db, int(form.getfirst('id')))
if form.getfirst('action') == 'add':
	if 'eventType' in form:
		account.addSubscription(db, form.getfirst('eventType'), account.getUser(), form.getfirst('filter-doc-tag'))
	else:
		forms.showModifyForm(db, -1)
		done = 1
if form.getfirst('action') == 'listall' and account.getAdmin(db):
	forms.showAllSubscriptions(db)
	done = 1
if form.getfirst('action') == 'help':
	forms.showHelp()
	done = 1

if not done:
	forms.showSubscriptions(db, account.getUser())

template.footer()
db.close()
