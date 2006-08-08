# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser
# See LICENSE file in the root of the source distribution for details

import ConfigParser

CONFIG_FILES = [
        '/etc/ietfnotify/ietfnotify.conf',
        'ietfnotifyd.conf',
    ]

config = ConfigParser.ConfigParser()
configfile = None

def readconfig():
    for file in CONFIG_FILES:
        try:
            fp = open(file, 'r')
            config.readfp(fp)
            fp.close()
            configfile = file
            return
        except:
            pass
    if not configfile:
        raise Exception("Could not find a configuration file")

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
	fd = open(configfile, 'w')
	config.write(fd)
	fd.close()

readconfig()
