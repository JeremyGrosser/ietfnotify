# ietfnotify - Receives, archives, and sends notifications related to IETF
#              events, drafts, working groups, etc.
# Copyright (C) 2006 Jeremy Grosser

import account

def header(db):
	print '''Content-type: text/html\n\n
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
 <title>IETF Event Notifier</title>
 <style type="text/css">
 body {
 	font-family: "Arial", sans-serif;
	font-size: 10pt;
	color: #000;
	background-color: #FFF;
	margin: 0;
 }

 #header {
 	background-color: #227;
 	left: 0;
	right: 0;
	top: 0;
	height: 30px;
	padding: 5px;
 }

 #logo {
 	font-family: "Futura", "Andale Mono", "Trebuchet MS", sans-serif;
	font-size: 18pt;
	color: #FFF;
 }

 #navigation {
 	float: left;
	border: 0;
	border-right: 1px;
	border-style: solid;
	border-color: #000;
	margin: 5px;
	margin-right: 10px;
	padding: 5px;
 }

 #content {
 	margin: 10px;
 }

 span.username {
 	font-style: bold;
	font-size: 12pt;
 }

 tr.gray { background-color: #CCC; }
 tr.white { background-color: #FFF; }

 tr.header { background-color: #BBF; }

 table {
	border-spacing: 0;
	border-collapse: collapse;
 }

 td, th {
	border: 1px;
	border-style: solid;
	border-color: #000;
	padding: 5px;
 }

 th { text-align: left; }

 a:link { color: #0000FF; text-decoration: none; }
 a:active { text-decoration: none; }
 a:visited { text-decoration: none; }
 a:hover { text-decoration: underline; }
</style>
 <script language="JavaScript">
 function disableAddress() {
 	if(document.modifyForm.eventType.value == "html_email" || document.modifyForm.eventType.value == "plain_email") {
		document.modifyForm.param.disabled = true
	}else{
		document.modifyForm.param.disabled = false
	}
 }
 </script>
</head>

<body onLoad="disableAddress()">

<div id="header">
 <div id="logo">IETF Event Notifier</div>
</div>

<div id="navigation">
'''
	if account.getUser() == '':
		print '<strong>Not logged in</strong>'
	else:
		print '<strong>' + account.getUser() + '</strong>'
		print '<p><a href="?">List subscriptions</a>'
		if account.getAdmin(db):
			print '<br /><a href="?action=listall">List all subscriptions</a>'
		print '<br /><a href="?action=add">New notification</a>'
		print '<br /><a href="?action=help">Help</a></p>'
	print '''</div>

<div id="content">'''

def footer():
	print '''</div>
</body>
</html>
'''
