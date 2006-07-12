# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import os

import util
import config
import notifier
import log
import message

def buildUUIDCache():
	log.log(log.NORMAL, 'Building UUID cache')
	listing = os.listdir(config.get('archive', 'uuid_dir'))
	for file in listing:
		st = os.stat(config.get('archive', 'uuid_dir') + '/' + file)
		notifier.uuidcache.append( (file, st[9]) ) # ctime
	notifier.uuidcache.sort()
	notifier.uuidcache = notifier.uuidcache[:config.getint('notify-atom', 'feedlength')]

def uuidArchive(uuid, parsed):
	log.log(log.NORMAL, 'Archive/UUID: ' + parsed['doc-tag'][0])
	os.chdir(config.get('archive', 'uuid_dir'))
	fd = open(uuid, 'w+')
	for key in parsed:
		for i in range(0, len(parsed[key])):
			fd.write(key + ': ' + parsed[key][i] + '\n')
	fd.close()

def getArchived(uuid):
	try:
		fd = open(config.get('archive', 'uuid_dir') + '/' + uuid, 'r')
		notparsed = ''
		for line in fd.readlines():
			notparsed += line
		fd.close()
	except IOError: return 0
	return message.parseMessage(notparsed, 1)

def dateArchive(uuid, parsed):
	log.log(log.NORMAL, 'Archive/Date: ' + parsed['doc-tag'][0])
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
	except OSError: pass

	try:
		os.symlink(symlink_source, symlink_dest)
	except OSError:
		os.remove(config.get('archive', 'uuid_dir') + '/' + uuid)
		log.log(log.ERROR, 'Unable to symlink the same uuid twice')
		return (1, 'Unable to symlink the same uuid twice')

archiveCallbacks = {}
archiveCallbacks['date'] = dateArchive

def archiveMessage(parsed):
	log.log(log.NORMAL, 'Archiving message: ' + parsed['doc-tag'][0])
	# Use the UUID from the event or generate one if the event didn't specify
	if 'event-uuid' in parsed:
		uuid = parsed['event-uuid'][0]
	else:
		uuid = util.makeUUID()

	# Notification MUST be archived by UUID before any other format
	uuidArchive(uuid, parsed)

	for callback in archiveCallbacks:
		f = archiveCallbacks[callback]
		f(uuid, parsed)

	# Update the uuid cache
	notifier.uuidcache.insert(0, (uuid, 0))
	return (0, uuid)
