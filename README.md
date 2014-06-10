xsf-tools
=========

Automated tools for the management of XEPs at the XSF

Right now working towards automatically defering XEPs. For some thoughts on the workflow see:
http://logs.xmpp.org/editor/2014-06-10/#18:36:56

Usage example for xeputils in version 0.1:

	$ python
	Python 2.7.7rc1 (default, May 21 2014, 12:59:42) 
	[GCC 4.8.2] on linux2
	Type "help", "copyright", "credits" or "license" for more information.
	>>> import xeputils
	>>> x = xeputils.AllXEPs("../xmpp/extensions")
	Error while parsing /home/winfried/Data/werk/XMPP-BOSH/xmpp/extensions/xep-0037.xml
	Traceback (most recent call last):
	  File "xeputils.py", line 174, in __init__
	    self.xeps.append(XEPInfo(fle))
	  File "xeputils.py", line 125, in __init__
	    self.majorVersion = int(self.version.split('.')[0])
	ValueError: invalid literal for int() with base 10: 'Version 0'
	Error while parsing /home/winfried/Data/werk/XMPP-BOSH/xmpp/extensions/xep-0144.xml
	Traceback (most recent call last):
	  File "xeputils.py", line 174, in __init__
	    self.xeps.append(XEPInfo(fle))
	  File "xeputils.py", line 123, in __init__
	    self.date = datetime.datetime.strptime(dateString,"%Y-%m-%d")
	  File "/usr/lib/python2.7/_strptime.py", line 325, in _strptime
	    (data_string, format))
	ValueError: time data 'in progress, last updated 2012-06-19' does not match format '%Y-%m-%d'
	>>> x.getInterim()
	[XEP-0124, XEP-0206, XEP-0266]
	>>> x.getInterim()[0].pprint()
	XEP-0124
	  version             1.11rc3
	  type                Standards Track
	  title               Bidirectional-streams Over Synchronous HTTP (BOSH)
	  status              Draft
	  shortname           bosh
	  nr                  124
	  minorVersion        11rc3
	  majorVersion        1
	  lastcall            False
	  interim             True
	  depends             [u'RFC 1945', u'RFC 2616', u'RFC 3174']
	  date                2014-02-10 00:00:00
	  abstract            This specification defines a transport protocol that emulates the semantics of a long-lived, bidirectional TCP connection between two entities (such as a client and a server) by efficiently using multiple synchronous HTTP request/response pairs without requiring the use of frequent polling or chunked responses.
	>>> x.getExpired()
	[XEP-0279, XEP-0305, XEP-0313, XEP-0316, XEP-0317, XEP-0321, XEP-0328]
	>>> for i in x.getExpired():
	...     print i.date
	... 
	2013-04-17 00:00:00
	2013-03-01 00:00:00
	2013-05-31 00:00:00
	2013-01-03 00:00:00
	2013-01-03 00:00:00
	2013-04-16 00:00:00
	2013-05-28 00:00:00


