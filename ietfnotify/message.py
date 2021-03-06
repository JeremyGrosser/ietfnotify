# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import django.conf
django.conf.settings.configure()
import django.template

import _mysql
import re
import sets

import util
import config
import log
import archive
import os.path

def updateFilters(parsed):
	log.log(log.DEBUG, 'Updating filters list in database')
	db = _mysql.connect(config.get('notifier', 'mysqlhost'), config.get('notifier', 'mysqluser'), config.get('notifier', 'mysqlpass'), config.get('notifier', 'mysqldb'))

	db.query('SELECT field FROM eventTypes WHERE type="filter"')
	res = db.store_result()

	store = []
	for storedField in res.fetch_row(0):
	 	store.append(storedField[0])

	parsed = parsed.keys()
	for eventField in parsed:
		if not eventField in store:
			log.log(log.DEBUG, 'Field "' + eventField + '" does not exist in the database, it will be added.')
			db.query('INSERT INTO eventTypes SET field="' + eventField + '", type="filter", admin=0')
	
	db.close()

def renderMessage(templateFile, parsed):
	log.log(log.DEBUG, 'Rendering django template (' + templateFile + ')')

	# Reformat the data into something django templates can work with
	fields = []
	attrib = {}
	date = {}
	keys = parsed.keys()
	keys.sort()
	for field in keys:
		attr = field.replace("-", "")
		value = parsed[field][0]
		valuedate = re.split(";([12][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])$", value)

		if len(valuedate) >= 2:
			value, date[attr] = valuedate[:2]
		value = value.replace("\\n", "\n   ").replace("\\x27", "'").replace("\\\\", "\\")
		fields.append([field, value])
		attrib[attr] = value
	
	# Read the template file
	template = ''
	fd = open(os.path.join(config.get('notifier', 'templatepath'), templateFile), 'r')
	template = fd.read()
	fd.close()

	# Create the django objects and render
	template = django.template.Template(template)
	context = django.template.Context({'fields': fields, 'attrib': attrib})
	return template.render(context)

def renderList(templateFile, uuidList):
	log.log(log.DEBUG, 'Rendering django list (' + templateFile + ')')
	
	# Turn a list of UUIDs into a list of tuples (tag, date)
	eventList = []
	for uuid in uuidList:
		parsed = archive.getArchived(uuid)
		if ('doc-tag' in parsed) and ('event-date' in parsed):
			eventList.append( (parsed['doc-tag'], parsed['event-date']) )
		else:
			log.log(log.ERROR, 'Missing doc-tag or event-date in archive (uuid:' + uuid + ')')

	# Read the template file
	template = ''
	fd = open(os.path.join(config.get('notifier', 'templatepath'), templateFile), 'r')
	template = fd.read()
	fd.close()

	# Create django objects and render
	template = django.template.Template(template)
	context = django.template.Context({'entries': eventList, 'updated': eventList[-1][1][0], 'feed_uuid': util.makeUUID()})
	return template.render(context)

def removeHidden(db, parsed):
	db.query('SELECT field FROM eventTypes WHERE type="filter" AND admin=1')
	res = db.store_result()

        if res:
            for field in res.fetch_row():
                try:
                    del parsed[field][0]
                except:
                    pass                # XXX needs further investigation

	return parsed
	
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
		parsed['event-date'] = [util.makeTimestamp()]

	# Strip off the field date tag
	#datere = re.compile(';[12][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$')
	#for field in parsed:
	#	for value in field:
	#		res = datere.search(parsed)
	#		if res:
	#			date = value[res.start:]
	#			value = value[:res.start]

	return parsed

def parseChanges(parsed, changeField):
	changes = {}
	for change in parsed[changeField][0].split(' '):
		changes[change] = 1
	return changes

def checkRequired(parsed):
	log.log(log.DEBUG, 'Checking required fields')
	if not 'doc-tag' in parsed:
		log.log(log.ERROR, 'No tag specified')
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
						log.log(log.ERROR, 'Required field "' + field + '" is missing')
						return (1, 'Required field "' + field + '" is missing')
			elif i[0] == 'optional':
				return (0, '')
				#optional_fields = i[1].split(', ')
				#for field in optional_fields:
				#	if field in parsed:
				#		pass
			else:
				log.log(log.ERROR, 'Unknown definition in config: ' + repr(i))
				return (1, 'Unknown definition in config: ' + repr(i))
	else:
		log.log(log.ERROR, 'Event type not specified in config file. Adding section. All fields will be added as optional. Fix this soon.')
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
