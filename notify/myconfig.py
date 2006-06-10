import ConfigParser

CONFIG_FILE = 'server.conf'

config = ConfigParser.ConfigParser()
fp = open(CONFIG_FILE, 'r')
config.readfp(fp)
fp.close()

def getint(section, key):
	return config.getint(section, key)

def get(section, key):
	return config.get(section, key)
