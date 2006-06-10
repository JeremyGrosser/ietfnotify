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

def checkRequired(parsed):
	if not 'tag' in parsed:
		return (1, 'No tag specified')
	tag = parsed['tag'][0].split('-', 1)
	event_type = tag[0]

	if config.has_section('fields-' + event_type):
		items = config.items('fields-' + event_type)
		for i in items:
			if i[0] == 'required':
				required_fields = i[1].split(', ')
				for field in required_fields:
					if not field in parsed:
						return (1, 'Required field "' + field + '" is missing')
			elif i[0] == 'optional':
				return (0, '')
				#optional_fields = i[1].split(', ')
				#for field in optional_fields:
				#	if field in parsed:
				#		pass
			else:
				return (1, 'Unknown definition in config: ' + repr(i))
	else:
		print 'Event type not specified in config file. Adding section. All fields will be added as optional. Fix this soon.'
		config.add_section('fields-' + event_type)
		oldkey = ''
		for key in parsed:
			if oldkey == '':
				newkey = key
			else:
				newkey = oldkey + ', ' + key
			config.set('fields-' + event_type, 'optional', newkey)
			oldkey = config.get('fields-' + event_type, 'optional')
		config.write()
		return (0, '')
