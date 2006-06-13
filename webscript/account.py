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

def getSubscriptions(db, username):
	ret = []
	db.query('SELECT id,username,type,target,pattern FROM subscriptions WHERE username=\'' + username + '\'')
	subs = db.store_result()
	return subs

def getSubscription(db, recordid):
	if getAdmin(db):
		db.query('SELECT username,type,target,pattern FROM subscriptions WHERE id=' + str(recordid))
	else:
		db.query('SELECT username,type,target,pattern FROM subscriptions WHERE username=\'' + getUser() + '\' AND id=' + str(recordid))
	sub = db.store_result()
	return sub

def getAllSubscriptions(db):
	if getAdmin(db):
		db.query('SELECT * FROM subscriptions')
		sub = db.store_result()
		return sub
	else:
		return None

def addSubscription(db, eventType, param, pattern):
	if eventType == None or param == None:
		return
	if pattern == None or len(pattern) > 128:
		pattern = ''
	db.query('INSERT INTO subscriptions SET username=\'' + getUser() + '\', type=\'' + sanitize(eventType) + '\', target=\'' + sanitize(param) + '\', pattern=\'' + regex_sanitize(pattern) + '\'')

def updateSubscription(db, recordid, eventType, param, pattern):
	if eventType == None or param == None:
		return
	if pattern == None or len(pattern) > 128:
		pattern = ''
	db.query('UPDATE subscriptions SET type=\'' + sanitize(eventType) + '\', target=\'' + sanitize(param) + '\', pattern=\'' + regex_sanitize(pattern) + '\' WHERE id=' + str(recordid) + ' AND username=\'' + getUser() + '\'')

def removeSubscription(db, recordid):
	db.query('DELETE FROM subscriptions WHERE id=' + str(recordid) + ' AND username=\'' + getUser() + '\'')
