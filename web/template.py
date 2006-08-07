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

	print '<a href="?action=viewarchive">Last 24 hours</a>'
	if account.getAdmin(db):
		print ' | <a href="?action=listall">List all subscriptions</a> |'
		print '<a href="?action=listfields">Edit filter fields</a>'
	print '</div>'

def footer():
	fd = open('resources/footer.html', 'r')
	print fd.read()
	fd.close()
