import os
import _mysql

def getUser():
	if 'REMOTE_USER' in os.environ:
		return os.environ['REMOTE_USER']
	return ''

def getAdmin(db):
	db.query('SELECT is_admin FROM subscriptions WHERE username=\'' + getUser() + '\'')
	res = db.store_result()
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
	if pattern == None:
		pattern = ''
	db.query('INSERT INTO subscriptions SET username=\'' + getUser() + '\', type=\'' + eventType + '\', target=\'' + param + '\', pattern=\'' + pattern + '\'')

def updateSubscription(db, recordid, eventType, param, pattern):
	if eventType == None or param == None:
		return
	if pattern == None:
		pattern = ''
	db.query('UPDATE subscriptions SET type=\'' + eventType + '\', target=\'' + param + '\', pattern=\'' + pattern + '\' WHERE id=' + str(recordid) + ' AND username=\'' + getUser() + '\'')

def removeSubscription(db, recordid):
	db.query('DELETE FROM subscriptions WHERE id=' + str(recordid) + ' AND username=\'' + getUser() + '\'')
