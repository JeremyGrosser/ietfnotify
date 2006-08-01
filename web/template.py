# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import account

def header(db):
	print 'Content-type: text/html\n\n'
	fd = open('resources/header.html', 'r')
	print fd.read()
	fd.close()

	fd = open('/www/tools.ietf.org/inc/narrow-menu-col.html', 'r')
	print fd.read()
	fd.close()

	print '<td><div class="content">'

	fd = open('resources/topnav.html', 'r')
	print fd.read()
	fd.close()

	#print '<div id="notify_actions">'
	#if account.getUser() == '':
	#	print '<strong>Not logged in</strong>'
	#else:
	#	print '<strong>' + account.getUser() + '</strong>'
	#	print '<p><a href="?">List subscriptions</a>'
	#	print '<br /><a href="?action=viewarchive">Search archives</a>'
	#	if account.getAdmin(db):
	#		print '<br /><a href="?action=listall">List all subscriptions</a>'
	#		print '<br /><a href="?action=listfields">Edit filter fields</a>'
	#	print '<br /><a href="?action=add">New notification</a>'
	#	print '<br /><a href="?action=help">Help</a></p>'
	#print '''</div>'''

def footer():
	fd = open('resources/footer.html', 'r')
	print fd.read()
	fd.close()
