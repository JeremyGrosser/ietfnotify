# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import os

import util
import config
import notifier
import log

def buildUUIDCache():
	log.log(log.NORMAL, 'Building UUID cache')
	listing = os.listdir(config.get('archive', 'uuid_dir'))
	for file in listing:
		st = os.stat(config.get('archive', 'uuid_dir') + '/' + file)
		notifier.uuidcache.append( (file, st[9]) ) # ctime
	notifier.uuidcache.sort()
	notifier.uuidcache = notifier.uuidcache[:config.getint('notify-atom', 'feedlength')]

def archiveMessage(parsed):
	log.log(log.NORMAL, 'Archiving message: ' + parsed['doc-tag'][0])
	# Use the UUID from the event or generate one if the event didn't specify
	if 'event-uuid' in parsed:
		uuid = parsed['event-uuid'][0]
	else:
		uuid = util.makeUUID()

	# Write the event to a file named with the UUID
	os.chdir(config.get('archive', 'uuid_dir'))
	fd = open(uuid, 'w+')
	for key in parsed:
		for i in range(0, len(parsed[key])):
			fd.write(key + ': ' + parsed[key][i] + '\n')
	fd.close()

	# Symlink from the date file structure to the uuid file
	if 'event-date' in parsed:
		year = parsed['event-date'][0][:4]
		month = parsed['event-date'][0][8:10]
	else:
		year = gmtime()[0]
		month = gmtime()[1]
	symlink_source = config.get('archive', 'uuid_dir') + '/' + uuid
	symlink_dest = config.get('archive', 'date_dir') + '/' + year + '/' + month + '/' + uuid

	try:
		os.makedirs(config.get('archive', 'date_dir') + '/' + year + '/' + month)
	except OSError: log.log(log.ERROR, 'Date directory already exists (' + config.get('archive', 'date_dir') + '/' + year + '/' + month + ')')

	try:
		os.symlink(symlink_source, symlink_dest)
	except OSError:
		os.remove(config.get('archive', 'uuid_dir') + '/' + uuid)
		log.log(log.ERROR, 'Unable to symlink the same uuid twice')
		return (1, 'Unable to symlink the same uuid twice')

	# Update the uuid cache
	notifier.uuidcache.insert(0, (uuid, 0))
	return (0, uuid)
