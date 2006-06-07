fd = open('../subscriptions.csv', 'r')
subscriptions = fd.readlines()
fd.close()

def getSubscriptions(username, password):
	ret = []
	for line in subscriptions:
		sub = line.split(',')
		if sub[1] == username and sub[2] == password:
			ret.append(sub)
	return ret
