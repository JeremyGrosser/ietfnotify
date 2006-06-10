import util

def parseMessage(msg, keepdate):
	lines = msg.split('\n')
	parsed = {}

	# Make some sense of the data
	for line in lines:
		if line.find(':') == -1:
			break
		line = line.split(':', 1)
		line[0] = line[0].lower()
		line[1] = line[1][1:]
		if line[0] in parsed:
			parsed[line[0]].append(line[1])
		else:
			parsed[line[0]] = [line[1]]
	
	# Generate a timestamp
	if not keepdate:
		parsed['date'] = [util.makeTimestamp()]
	return parsed
