# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

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
	db.query('SELECT id,username,type,target FROM subscriptions WHERE username=\'' + getUser() + '\'')
	subs = db.store_result()
	return subs

def getSubscription(db, recordid):
	if getAdmin(db):
		db.query('SELECT username,type,target FROM subscriptions WHERE id=' + str(recordid))
	else:
		db.query('SELECT username,type,target FROM subscriptions WHERE username=\'' + getUser() + '\' AND id=' + str(recordid))
	sub = db.store_result()
	return sub

def getFilters(db, recordid):
	# Get all possible filter types
	db.query('SELECT field FROM eventTypes WHERE type="filter" AND admin=0')
	fields = db.store_result()

	if getAdmin(db):
		db.query('SELECT field, pattern FROM filters WHERE parent_id=' + str(recordid))
	else:
		db.query('SELECT field, pattern FROM filters WHERE parent_id=' + str(recordid) + ' AND username="' + getUser() + '"')
	filters = db.store_result()

	result = {}
	for field in fields.fetch_row(0):
		result[field[0]] = ''
	for filter in filters.fetch_row(0):
		result[filter[0]] = filter[1]
	return result

def getTagFilter(db, recordid):
	if getAdmin(db):
		db.query('SELECT * FROM filters WHERE parent_id=' + str(recordid) + ' AND field="doc-tag"')
	else:
		db.query('SELECT * FROM filters WHERE parent_id=' + str(recordid) + ' AND field="doc-tag" AND username="' + getUser() + '"')

	filter = db.store_result()
	if filter.num_rows() > 0:
		return filter.fetch_row()[0][2]
	else:
		return ''

def getAllSubscriptions(db):
	if getAdmin(db):
		db.query('SELECT * FROM subscriptions')
		sub = db.store_result()
		return sub
	else:
		return None

def addSubscription(db, eventType, param):
	eventType = sanitize(eventType)
	param = sanitize(param)
	if eventType == None or param == None:
		return
	db.query('INSERT INTO subscriptions SET username=\'' + getUser() + '\', type=\'' + eventType + '\', target=\'' + param + '\'')

def updateSubscription(db, recordid, eventType, param, filters):
	# Sanitize the inputs
	eventType = regex_sanitize(eventType)
	param = regex_sanitize(param)
	for field in filters:
		filters[field] = regex_sanitize(filters[field])
		# Check to see if the filter already exists
		db.query('SELECT id FROM filters WHERE type="' + eventType + '" AND field="' + field + '" AND parent_id=' + str(recordid))
		res = db.store_result()
		if res.num_rows() > 0:
			# Modify existing filter
			existsid = res.fetch_row()
			existsid = existsid[0][0]
			db.query('UPDATE filters SET pattern="' + filters[field] + '" WHERE id=' + str(existsid))
		else:
			# Create a new filter
			db.query('INSERT INTO filters SET type="' + eventType + '", pattern="' +filters[field] + '", field="' + field + '", parent_id=' + str(recordid)) 

	# Make sure we have the right data
	if eventType == None or param == None:
		return
	db.query('UPDATE subscriptions SET type="' + eventType + '", target="' + param + '" WHERE id=' + str(recordid) + ' AND username="' + getUser() + '"')

def removeSubscription(db, recordid):
	db.query('DELETE FROM subscriptions WHERE id=' + str(recordid) + ' AND username="' + getUser() + '"')
	db.query('DELETE FROM filters WHERE parent_id=' + str(recordid))

def removeFilters(db, fields):
	for field in fields:
		db.query('UPDATE eventTypes SET admin=1 WHERE field="' + field + '" AND type="filter"')
