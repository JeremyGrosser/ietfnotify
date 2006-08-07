# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import os
import _mysql
import re

def regex_sanitize(pattern):
	regex = re.compile('\\\\$|(\'|\")')
	if regex.search(pattern):
		return ''
	else:
		return pattern

def sanitize(dirty):
	regex = re.compile('^([a-z]|[A-Z]|[0-9]|[_@\\.])*$')
	if regex.search(dirty):
		return dirty
	else:
		return ''

def getUser():
	if 'REMOTE_USER' in os.environ:
		return os.environ['REMOTE_USER']
	return ''

def getAdmin(db):
	db.query('SELECT is_admin FROM subscriptions WHERE username=\'' + getUser() + '\'')
	res = db.store_result()
	if res.num_rows() < 1:
		return 0
	else:
		return int(res.fetch_row()[0][0])

def getSubscriptions(db):
	ret = []
	db.query('SELECT id,username,type,target,enabled,name FROM subscriptions WHERE username=\'' + getUser() + '\'')
	subs = db.store_result()

	count = 0
	for sub in subs.fetch_row(0):
		dict = {}
		count += 1
		if count % 2:
			dict['color'] = 'gray'
		else:
			dict['color'] = 'white'

		dict['id'] = sub[0]
		dict['notification'] = sub[2]
		dict['address'] = sub[3]
		dict['filter'] = getTagFilter(db, sub[0])
		dict['name'] = sub[5]

		if sub[4] == '1':
			dict['enableaction'] = 'Disable'
		else:
			dict['enableaction'] = 'Enable'
		ret.append(dict)
	return ret

def getAllSubscriptions(db):
	ret = []
	db.query('SELECT id,username,type,target,enabled,name FROM subscriptions')
	subs = db.store_result()

	count = 0
	for sub in subs.fetch_row(0):
		dict = {}
		count += 1
		if count % 2:
			dict['color'] = 'gray'
		else:
			dict['color'] = 'white'

		dict['id'] = sub[0]
		dict['notification'] = sub[2]
		dict['address'] = sub[3]
		dict['filter'] = getTagFilter(db, sub[0])
		dict['name'] = sub[5]

		if sub[4] == '1':
			dict['enableaction'] = 'Disable'
		else:
			dict['enableaction'] = 'Enable'
		ret.append(dict)
	return ret

def getSubscription(db, recordid):
	if getAdmin(db):
		db.query('SELECT username,type,target,name FROM subscriptions WHERE id=' + str(recordid))
	else:
		db.query('SELECT username,type,target,name FROM subscriptions WHERE username=\'' + getUser() + '\' AND id=' + str(recordid))
	sub = db.store_result()
	return sub

def getFilters(db, recordid):
	# Get all possible filter types
	db.query('SELECT field FROM eventTypes WHERE type="filter" AND admin=0')
	fields = db.store_result()

	if getAdmin(db):
		db.query('SELECT field, pattern, id FROM filters WHERE parent_id=' + str(recordid))
	else:
		db.query('SELECT field, pattern, id FROM filters WHERE parent_id=' + str(recordid) + ' AND username="' + getUser() + '"')
	filters = db.store_result()

	result = {}
	for field in fields.fetch_row(0):
		result[field[0]] = ''
	for filter in filters.fetch_row(0):
		result[filter[0]] = filter[1]
	return result

# This method is no longer used!
def removeFilter(db, parentid, field):
	field = regex_sanitize(field)
	if getAdmin(db):
		db.query('DELETE FROM filters WHERE field="' + field + '" AND parent_id=' + str(parentid))
	else:
		db.query('SELECT * FROM subscriptions WHERE id=' + str(parentid) + ' AND username="' + getUser() + '"')
		res = db.store_result()
		if res.num_rows() > 0:
			db.query('DELETE FROM filters WHERE field="' + field + '" AND parent_id=' + str(parentid))

def getTagFilter(db, recordid):
	db.query('SELECT * FROM filters WHERE parent_id=' + str(recordid) + ' AND field="doc-tag"')

	filter = db.store_result()
	if filter.num_rows() > 0:
		return filter.fetch_row()[0][2]
	else:
		return ''

def addSubscription(db, eventType, param, name, filters):
	eventType = sanitize(eventType)
	param = sanitize(param)
	name = regex_sanitize(name)
	if eventType == None or param == None:
		return
	db.query('INSERT INTO subscriptions SET username=\'' + getUser() + '\', type=\'' + eventType + '\', target=\'' + param + '\', name=\'' + name + '\'')

	db.query('SELECT LAST_INSERT_ID()')
	res = db.store_result()
	recordid = res.fetch_row()
	recordid = int(recordid[0][0])

	for field in filters:
		db.query('INSERT INTO filters SET type="' + eventType + '", pattern="' + filters[field] + '", field="' + field + '", parent_id=' + str(recordid))

def updateSubscription(db, recordid, eventType, param, filters, name):
	# Sanitize the inputs
	eventType = regex_sanitize(eventType)
	param = regex_sanitize(param)
	name = regex_sanitize(name)
	db.query('DELETE FROM filters WHERE parent_id=' + str(recordid))
	for field in filters:
		filters[field] = regex_sanitize(filters[field])
		# Create a new filter
		db.query('INSERT INTO filters SET type="' + eventType + '", pattern="' +filters[field] + '", field="' + field + '", parent_id=' + str(recordid)) 

	# Make sure we have the right data
	if eventType == None or param == None:
		return
	db.query('UPDATE subscriptions SET type="' + eventType + '", target="' + param + '", name="' + name + '" WHERE id=' + str(recordid) + ' AND username="' + getUser() + '"')

def removeSubscription(db, recordid):
	db.query('DELETE FROM subscriptions WHERE id=' + str(recordid) + ' AND username="' + getUser() + '"')
	db.query('DELETE FROM filters WHERE parent_id=' + str(recordid))

def enableSubscription(db, recordid):
	if getAdmin(db):
		db.query('UPDATE subscriptions SET enabled=1 WHERE id=' + str(recordid))
	else:
		db.query('UPDATE subscriptions SET enabled=1 WHERE id=' + str(recordid) + ' AND username="' + getUser() + '"')

def disableSubscription(db, recordid):
	if getAdmin(db):
		db.query('UPDATE subscriptions SET enabled=0 WHERE id=' + str(recordid))
	else:
		db.query('UPDATE subscriptions SET enabled=0 WHERE id=' + str(recordid) + ' AND username="' + getUser() + '"')

def duplicateSubscription(db, recordid):
	if getAdmin(db):
		db.query('SELECT * FROM subscriptions WHERE id=' + str(recordid))
	else:
		db.query('SELECT * FROM subscriptions WHERE id=' + str(recordid) + ' AND username="' + getUser() + '"')
	original = db.store_result()
	db.query('SELECT * FROM filters WHERE parent_id=' + str(recordid))
	filters = db.store_result()

	if original.num_rows() > 0:
		db.query('INSERT INTO subscriptions (username,type,target,is_admin,name) SELECT username,type,target,is_admin,name FROM subscriptions WHERE id=' + str(recordid))
		db.query('SELECT LAST_INSERT_ID()')
		newid = db.store_result()
		newidrow = newid.fetch_row()
		newid = newidrow[0][0]

		db.query('INSERT INTO filters (type,pattern,field) SELECT type,pattern,field FROM filters WHERE parent_id=' + str(recordid))
		db.query('UPDATE filters SET parent_id=' + newid + ' WHERE id=LAST_INSERT_ID()')
	else:
		print 'Error: Subscription does not exist<br />'

def removeFilters(db, fields):
	for field in fields:
		db.query('UPDATE eventTypes SET admin=1 WHERE field="' + field + '" AND type="filter"')
