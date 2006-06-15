# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import ConfigParser
import log

CONFIG_FILE = 'server.conf'

log.log(log.NORMAL, 'Reading config file: ' + CONFIG_FILE)
config = ConfigParser.ConfigParser()
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
