# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import ConfigParser

CONFIG_FILE = '/home/jeremy/src/ietfnotify/server.conf'
config = ConfigParser.ConfigParser()

def readconfig():
	fp = open(CONFIG_FILE, 'r')
	config.readfp(fp)
	fp.close()

def getint(section, key):
	return config.getint(section, key)

def get(section, key):
	return config.get(section, key)

def has_section(section):
	return config.has_section(section)

def items(section):
	return config.items(section)

def add_section(section):
	return config.add_section(section)

def set(section, key, value):
	return config.set(section, key, value)

def write():
	fd = open(CONFIG_FILE, 'w')
	config.write(fd)
	fd.close()

readconfig()
