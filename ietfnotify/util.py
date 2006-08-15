# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import time
import os
import config

fieldmap = []

def makeTimestamp():
	return time.strftime('%Y-%m-%dT%H:%M:%S%:z')

def makeUUID():
	uuid = os.popen('uuidgen -t', 'r').readlines()
	uuid = uuid[0]
	return uuid[:-1]

def encodeBitstring(fields):
	fieldmap = loadFieldMap()
	bitstring = []
	for field in fields:
		# Figure out what string index the field is in
		if field in fieldmap:
			bit = fieldmap.index(field)
		else:
			# The field isn't known, add it to the map and append to the mapfile
			fieldmap.append(field)
			bit = len(fieldmap) - 1
			fd = open(config.get('general', 'mapfile'), 'a')
			fd.write(field + '\n')
			fd.close()

		# Pad the bitstring if necessary
		for i in range(len(bitstring), bit + 1):
			bitstring.append(0)

		# Load the bit values into the string
		if fields[field] == 'on':
			bitstring[bit] = 1
		else:
			bitstring[bit] = 0
	
	# Convert the list to a literal string
	realstring = ''
	for bit in bitstring:
		realstring += str(bit)
	
	return realstring

def decodeBitstring(bitstring):
	fieldmap = loadFieldMap()
	fields = {}
	for i in range(0, len(bitstring)):
		fields[fieldmap[i]] = bitstring[i]
	return fields

def loadFieldMap():
	map = []
	fd = open(config.get('general', 'mapfile'), 'r')
	for line in fd.readlines():
		map.append(line[:-1])
	fd.close()
	return map
