import os

import util
import config

def archiveMessage(parsed):
	# Generate a new UUID
	uuid = util.makeUUID()

	# Write the event to a file named with the UUID
	os.chdir(config.get('archive', 'uuid_dir'))
	fd = open(uuid, 'w+')
	for key in parsed:
		for i in range(0, len(parsed[key])):
			fd.write(key + ': ' + parsed[key][i] + '\n')
	fd.close()

	# Symlink from the date file structure to the uuid file
	year = parsed['date'][0][:4]
	month = parsed['date'][0][8:10]
	symlink_source = config.get('archive', 'uuid_dir') + '/' + uuid
	symlink_dest = config.get('archive', 'date_dir') + '/' + year + '/' + month + '/' + uuid

	try:
		os.makedirs(config.get('archive', 'date_dir') + '/' + year + '/' + month)
	except OSError: pass

	try:
		os.symlink(symlink_source, symlink_dest)
	except OSError:
		os.remove(config.get('archive', 'uuid_dir') + '/' + uuid)
		return (1, 'Unable to symlink the same uuid twice')

	# Update the uuid cache
	#uuidcache.insert(0, (uuid, 0))
	return (0, uuid)
