def header():
	print '''Content-type: text/html\n\n
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
	padding: 5px;
 }

 #content {
 	margin: 10px;
 }

 span.username {
 	font-style: bold;
	font-size: 12pt;
 }

 a:link { color: #0000FF; text-decoration: none; }
 a:active { text-decoration: none; }
 a:visited { text-decoration: none; }
 a:hover { text-decoration: underline; }
</style>

<body>

<div id="header">
 <div id="logo">IETF Event Notifier</div>
</div>

<div id="navigation">
 <strong>nobody@example.org</strong>
 <p><a href="?action=add">Add notification</a>
 <br /><a href="?action=remove">Remove notification</a>
 <br /><a href="?action=modify">Modify notification</a>
 <br /><a href="?action=editprofile">Edit profile</a>
 <br /><a href="?action=signout">Sign out</a></p>
</div>

<div id="content">'''

def footer():
	print '''</div>
</body>
</html>
'''
