# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
						  
import util
import config

def htmlMessage(parsed):
	msg = '''<html>
<head>
 <title>''' + parsed['doc-tag'][0] + '''</title>
 <style type="text/css">
 table {
 	border-spacing: 0;
	border-collapse: collapse;
 }

 td.field1 { background-color: #AAF; }
 td.value1 { background-color: #AFA; }
 td.field2 { background-color: #99C; }
 td.value2 { background-color: #9C9; }

 td {
 	border: 1px;
	border-style: solid;
	border-color: #000;
	padding: 5px;
 }
 </style>
</head>

<body>
<table>'''
	color = 1
	for field in parsed:
		for i in parsed[field]:
			if color == '2':	color = str(1)
			else:				color = str(2)
			msg += '''<tr>
 <td class="field''' + color + '''">''' + field + '''</td>
 <td class="value''' + color + '''">''' + i + '''</td>
</tr>'''
	msg += '''</table>
</body>
</html>'''
	return msg

def textMessage(parsed, newline='\n'):
	msg = ''
	for field in parsed:
		for i in parsed[field]:
			msg += field + ' - ' + i + newline
	return msg

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
	if not 'doc-tag' in parsed:
		return (1, 'No tag specified')
	tag = parsed['doc-tag'][0].split('-', 1)
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
