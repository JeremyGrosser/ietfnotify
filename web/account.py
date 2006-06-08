import os

def readSubscriptions():
	global subscriptions
	fd = open('../subscriptions.csv', 'r')
	subscriptions = fd.readlines()
	fd.close()

def getUser():
	return 'synack@csh.rit.edu'
	if 'REMOTE_USER' in os.environ:
		return os.environ['REMOTE_USER']
	return ''

def getSubscriptions(username):
	ret = []
	for line in subscriptions:
		line = line[:-1]
		sub = line.split(',')
		if sub[0] == username:
			ret.append(sub)
	return ret

def getAllSubscriptions():
	ret = []
	for line in subscriptions:
		line = line[:-1]
		sub = line.split(',')
		ret.append(sub)
	return ret

def joinSub(line, delim):
	ret = ''
	for i in line:
		ret += str(i) + delim
	return ret

def updateSubscription(id, eventType, param, pattern):
	user = getUser()

	if eventType == None or param == None:
		return

	if pattern == None:
		pattern = ''

	count = 0
	allsubs = getAllSubscriptions()
	for sub in allsubs:
		if count == id:
			print 'Found subscription in file<br />'
			sub[1] = eventType
			sub[2] = param
			sub[3] = pattern
		if sub[0] == user:
			count += 1
	subfile = open('../subscriptions.csv', 'w')
	for line in allsubs:
		newline = joinSub(line, ',')
		newline = newline[:-1]
		subfile.write(newline + '\n')
	subfile.close()
	readSubscriptions()

def removeSubscription(id):
        user = getUser()

        count = 0
        allsubs = getAllSubscriptions()
        for sub in allsubs:
                if count == id:
                        sub[1] = 'nosave'
                        break
                if sub[0] == user:
                        count += 1
        subfile = open('../subscriptions.csv', 'w')
        for line in allsubs:
		if not line[1] == 'nosave':
                	newline = joinSub(line, ',')
                	newline = newline[:-1]
                	subfile.write(newline + '\n')   
        subfile.close()
        readSubscriptions()

readSubscriptions()
