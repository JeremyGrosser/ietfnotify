#!/usr/bin/env python

from distutils.core import setup

setup(name='ietfnotify',
	version='0.01',
	description='IETF Event Notification Service',
	author='Jeremy Grosser',
	author_email='synack@csh.rit.edu',
	url='http://sourceforge.net/projects/ietfnotify',
	packages=['ietfnotify', 'ietfnotify.web'],
	scripts=['ietfnotifyd'],
	data_files=[('/etc/ietfnotify', 'doc/ietfnotify.conf'),
				('/etc/ietfnotify', 'templates/')]
	)
package_dir = {'ietfnotify': 'ietfnotify'}
