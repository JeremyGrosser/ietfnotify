def makeTimestamp():
	tz = time.strftime('%z')
	tz = '-' + tz[1:]
	tz = tz[:3] + ':' + tz[3:]
	return time.strftime('%Y-%d-%mT%H:%M:%S') + tz

def makeUUID():
	uuid = os.popen('uuidgen -t', 'r').readlines()
	uuid = uuid[0]
	return uuid[:-1]
