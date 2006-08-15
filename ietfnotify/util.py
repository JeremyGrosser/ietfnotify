# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import time
import os
import config

def makeTimestamp():
	return time.strftime('%Y-%m-%dT%H:%M:%S%:z')

def makeUUID():
	uuid = os.popen('uuidgen -t', 'r').readlines()
	uuid = uuid[0]
	return uuid[:-1]

def encodeBitstring(db, fields):
	bitstring = []
	for field in fields:
		# Figure out what string index the field is in
		db.query('SELECT id FROM eventTypes WHERE field="' + field + '"')
		res = db.store_result()
		if res.num_rows() > 0:
			bit = res.fetch_row()
			bit = int(bit[0][0])
		else:
			# The field isn't known, add it to the map and append to the mapfile
			bit = addField(db, field)

		# Pad the bitstring if necessary
		for i in range(len(bitstring), bit + 1):
			bitstring.append(0)

		# Load the bit value into the string
		if fields[field] == 'on':
			bitstring[bit] = 1
		else:
			bitstring[bit] = 0
	
	# Convert the list to a literal string
	realstring = ''
	for bit in bitstring:
		realstring += str(bit)
	
	return realstring

def decodeBitstring(db, bitstring):
	fields = {}
	for i in range(0, len(bitstring)):
		db.query('SELECT field FROM eventTypes WHERE id=' + str(i))
		res = db.store_result()
		if res.num_rows() > 0:
			field = res.fetch_row()
			field = field[0][0]
			fields[field] = bitstring[i]
	return fields

def addField(db, field):
	db.query('INSERT INTO eventTypes SET field="' + field + '", type="filter", admin=0, defaultIgnore=0')
	db.query('SELECT LAST_INSERT_ID()')
	res = db.store_result()
	last = res.fetch_row()
	last = last[0][0]
	return int(last)
