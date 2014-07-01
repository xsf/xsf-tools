# File: xeptable.py
# Version: 0.2
# Description: utility functions for handling XEPs
# Last Modified: 2014-06-19
# Based on scripts by:
#    Tobias Markmann (tm@ayena.de)
#    Peter Saint-Andre (stpeter@jabber.org)
# Authors:
#    Winfried Tilanus (winfried@tilanus.com)

## LICENSE ##
#
# Copyright (c) 1999 - 2014 XMPP Standards Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of tqhe Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
## END LICENSE ##

## creates a HTML table (for the human reader) and XML table (for bots)
class XEPTable:
	def __init__(self, filename, shortXMLfilename):
		self.filename = filename
		self.shortXMLfilename = shortXMLfilename
		
		try:
			self.tableFile = parse(filename)
		except:
			impl = getDOMImplementation()
			self.tableFile = impl.createDocument(None, "table", None)
			self.tableFile.getElementsByTagName("table")[0].setAttribute("class", "sortable")
			self.tableFile.getElementsByTagName("table")[0].setAttribute("id", "xeplist")
			self.tableFile.getElementsByTagName("table")[0].setAttribute("cellspacing", "0")
			self.tableFile.getElementsByTagName("table")[0].setAttribute("cellpadding", "3")
			self.tableFile.getElementsByTagName("table")[0].setAttribute("border", "1")
			
			header = parseString(
'''<tr class='xepheader'>
	<th align='left'>Number</th>
	<th align='left'>Name</th>
	<th align='left'>Type</th>
	<th align='left'>Status</th>
	<th align='left'>Date</th>
</tr>''')
			self.tableFile.getElementsByTagName("table")[0].appendChild(header.getElementsByTagName("tr")[0])
		
		try:
			self.botsFile = parse(shortXMLfilename)
		except:
			impl = getDOMImplementation()
			self.botsFile = impl.createDocument(None, "xeps", None)

	def save(self):
		f = open(self.filename, "wb")
		self.tableFile.getElementsByTagName("table")[0].normalize()
		f.write(self.tableFile.toxml())
		f.close()
		
		f = open(self.shortXMLfilename, "wb")
		self.botsFile.getElementsByTagName("xeps")[0].normalize()
		f.write(self.botsFile.toxml())
		f.close()

	def setXEP(self, info):
		## set for HTML table
		rows = self.tableFile.getElementsByTagName("tr")
		xeprow = 0
		for row in rows:
			if row.getAttribute("id") == "xep" + info.getNr():
				xeprow = row
				break
		
		if xeprow == 0:
			xeprow = self.tableFile.createElement("tr")
			self.tableFile.getElementsByTagName("table")[0].appendChild(xeprow)
			self.tableFile.getElementsByTagName("table")[0].appendChild(self.tableFile.createTextNode('''
'''))
			xeprow.setAttribute("id", "xep" + info.getNr())
			xeprow.setAttribute("class", "tablebody XEP-" + info.getStatus())
		else:
			xeprow.setAttribute("class", "tablebody XEP-" + info.getStatus())
			while(xeprow.hasChildNodes()):
				xeprow.removeChild(xeprow.firstChild)
		
		col = parseString('''<td valign='top'><a href='/extensions/xep-''' + info.getNr() + ".html'>XEP-" + info.getNr() + '''</a> <a href='/extensions/xep-''' + info.getNr() + '''.pdf'>(PDF)</a></td>''')
		xeprow.appendChild(col.getElementsByTagName("td")[0])
		
		col = parseString("<td valign='top'>" + info.getTitle() + "</td>")
		xeprow.appendChild(col.getElementsByTagName("td")[0])
		
		col = parseString("<td valign='top'>" + info.getType() + "</td>")
		xeprow.appendChild(col.getElementsByTagName("td")[0])
		
		col = parseString("<td valign='top'>" + info.getStatus() + "</td>")
		xeprow.appendChild(col.getElementsByTagName("td")[0])
		
		col = parseString("<td valign='top'>" + info.getDate() + "</td>")
		xeprow.appendChild(col.getElementsByTagName("td")[0])
		
		## set for bots file
		xeps = self.botsFile.getElementsByTagName("xep")
		xep = 0
		for xeps_xep in xeps:
			if xeps_xep.getElementsByTagName("number")[0].firstChild.data == info.getNr():
				xep = xeps_xep
				break
		
		if xep == 0:
			xep = self.botsFile.createElement("xep")
			self.botsFile.getElementsByTagName("xeps")[0].appendChild(xep)
			self.botsFile.getElementsByTagName("xeps")[0].appendChild(self.botsFile.createTextNode('''
'''))
		else:
			while(xep.hasChildNodes()):
				xep.removeChild(xep.firstChild)
		
		child = parseString("<number>" + info.getNr() + "</number>")
		xep.appendChild(child.getElementsByTagName("number")[0])
		
		child = parseString("<name>" + info.getTitle() + "</name>")
		xep.appendChild(child.getElementsByTagName("name")[0])
		
		child = parseString("<type>" + info.getType() + "</type>")
		xep.appendChild(child.getElementsByTagName("type")[0])
		
		child = parseString("<status>" + info.getStatus() + "</status>")
		xep.appendChild(child.getElementsByTagName("status")[0])
		
		child = parseString("<updated>" + info.getDate() + "</updated>")
		xep.appendChild(child.getElementsByTagName("updated")[0])
		
		child = parseString("<shortname>" + info.getShortname() + "</shortname>")
		xep.appendChild(child.getElementsByTagName("shortname")[0])
		
		child = parseString("<abstract>" + info.getAbstract() + "</abstract>")
		xep.appendChild(child.getElementsByTagName("abstract")[0])
