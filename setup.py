#!/usr/bin/env python

from distutils.core import setup

setup(name='ietfnotify',
	version='0.01',
	description='IETF Event Notification Service',
	author='Jeremy Grosser',
	author_email='synack@csh.rit.edu',
	url='http://sourceforge.net/projects/ietfnotify',
	packages=['ietfnotify', 'ietfnotify.web']
	scripts=['ietfnotifyd.py', 'web/index.cgi']
	data_files=[('/etc', 'doc/ietfnotify.conf')]
	)
package_dir = {'ietfnotify': 'ietfnotify'}
