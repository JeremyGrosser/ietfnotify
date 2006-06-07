#!/usr/bin/python
import template, subscriptions
import cgi

# DEBUGGING ONLY
import cgitb
cgitb.enable()
# DEBUGGING ONLY

form = cgi.FieldStorage()

template.header()
print 'Stuff goes here'
template.footer()
