#!/usr/bin/python
# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import sys
sys.path.insert(0, '/www/tools.ietf.org/tools/ietfnotify/')
#sys.path.insert(0, '/home/jeremy/src/ietfnotify/')

import ietfnotify.config as config
import ietfnotify.web.template as template
import ietfnotify.web.account as account
import ietfnotify.web.forms as forms
import cgi, os, _mysql

# DEBUG
import cgitb
cgitb.enable()
# DEBUG

form = cgi.FieldStorage()
db = _mysql.connect(config.get('notifier', 'mysqlhost'), config.get('notifier', 'mysqluser'), config.get('notifier', 'mysqlpass'), config.get('notifier', 'mysqldb'))

template.header(db)

done = 0

# If nobody is logged in
if account.getUser() == '':
	forms.showLoginMessage()
	done = 1

# Modify an existing notification
if form.getfirst('action') == 'modify' and 'id' in form:
	forms.showModifyForm(db, int(form.getfirst('id')))
	done = 1

# Affect changes on an existing notification
if form.getfirst('action') == 'update' and 'id' in form:
	filters = {} 
	ignore = {}
	for field in form:
		if field.startswith('filter-'):
			if field.endswith('-ignore'):
				ignore[field[7:-7]] = form.getfirst(field)
			else:
				filters[field[7:]] = form.getfirst(field)

	if form.getfirst('eventType') == 'html_email' or form.getfirst('eventType') == 'plain_email':
		account.updateSubscription(db, int(form.getfirst('id')), form.getfirst('eventType'), account.getUser(), filters, ignore, form.getfirst('name'))
	else:
		account.updateSubscription(db, int(form.getfirst('id')), form.getfirst('eventType'), form.getfirst('param'), filters, ignore, form.getfirst('name'))

# Remove an existing notification
if form.getfirst('action') == 'remove' and 'id' in form:
	account.removeSubscription(db, int(form.getfirst('id')))

# Create a new notification
if form.getfirst('action') == 'add':
	if 'eventType' in form:
		if not 'name' in form:
			name = ''
			print 'no name passed'
		else:
			name = form.getfirst('name')
			print 'name=' + name
		filters = {}
		for field in form:
			if field.startswith('filter-'):
				filters[field[7:]] = form.getfirst(field)

		account.addSubscription(db, form.getfirst('eventType'), account.getUser(), name, filters)
	else:
		forms.showModifyForm(db, -1)
		done = 1

# Admin only - Show all notifications
if form.getfirst('action') == 'listall' and account.getAdmin(db):
	forms.showAllSubscriptions(db)
	done = 1

# Show help page
if form.getfirst('action') == 'help':
	forms.showHelp()
	done = 1

# Hide specified fields from the user form
if form.getfirst('action') == 'removefields' and account.getAdmin(db):
	filters = []
	ignored = []
	for field in form:
		if field.startswith('filter-') and form.getfirst(field) == 'on':
			filters.append(field[7:])
		if field.startswith('ignore-') and form.getfirst(field) == 'on':
			ignored.append(field[7:])
	account.updateFilters(db, filters, ignored)
	forms.showFieldsList(db)
	done = 1

# List all known fields
if form.getfirst('action') == 'listfields' and account.getAdmin(db):
	forms.showFieldsList(db)
	done = 1

# View notification archives
if form.getfirst('action') == 'viewarchive':
	if 'year' in form and 'month' in form:
		forms.showArchived(int(form.getfirst('year')), int(form.getfirst('month')))
	else:
		forms.showArchiveSearch()
	done = 1

# Duplicate an existing subscription
if form.getfirst('action') == 'duplicate':
	account.duplicateSubscription(db, int(form.getfirst('id')))

# Enable/Disable a subscription
if form.getfirst('action') == 'Enable':
	account.enableSubscription(db, int(form.getfirst('id')))
if form.getfirst('action') == 'Disable':
	account.disableSubscription(db, int(form.getfirst('id')))

# Remove an existing filter from a notification
if form.getfirst('action') == 'removefilter':
	account.removeFilter(db, int(form.getfirst('id')), form.getfirst('field'))

# When all else fails, show the user's subscriptions
if not done:
	forms.showSubscriptions(db)

template.footer()
db.close()
