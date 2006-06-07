import os

fd = open('../subscriptions.csv', 'r')
subscriptions = fd.readlines()
fd.close()

def getUser():
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
