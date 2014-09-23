# File: xeptable.py
# Version: 0.2
# Description: utility functions for handling XEPs
# Last Modified: 2014-06-19
# Based on scripts by:
#    Tobias Markmann (tm@ayena.de)
#    Peter Saint-Andre (stpeter@jabber.org)
# Authors:
#    Winfried Tilanus (winfried@tilanus.com)

# LICENSE ##
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
# END LICENSE ##

from xml.dom.minidom import parse, parseString, Document, getDOMImplementation

HTMLTableHeader = """<table border="1" cellpadding="3" cellspacing="0" class="sortable" id="xeplist">
  <tr class="xepheader">
    <th align="left">Number</th>
    <th align="left">Name</th>
    <th align="left">Type</th>
    <th align="left">Status</th>
    <th align="left">Date</th>
  </tr>"""

HTMLTableRow = """
  <tr class="tablebody XEP-{status}" id="xep{number}">
    <td valign="top">
      <a href="/extensions/xep-{number}.html">XEP-0001</a> <a href="/extensions/xep-{number}.pdf">(PDF)</a>
    </td>
    <td valign="top">
      {name}
    </td>
    <td valign="top">
      {type}
    </td>
    <td valign="top">
      {status}
    </td>
    <td valign="top">
      {updated}
    </td>
  </tr>"""

HTMLTableFooter = """
</table>
"""


class XEPTable(object):

    """
    Creates a HTML table (for the human reader) and XML table (for bots)
    """

    def __init__(self, xmlfile=None):
        """
        Returns a XEPTable object, to manipulate the XML and HTML index
        tables of xeps.

        Arguments:
          xmlfile (str): XML file to read cached data from. Needed to update a
                         Single XEP in a set of existing indexes.
        """
        self.xmlfile = xmlfile
        if xmlfile:
            self.doc = parse(xmlfile)
        else:
            impl = getDOMImplementation()
            self.doc = impl.createDocument(None, "xeps", None)

    def updateXEP(self, xep):
        """
        If the XEP is already in the table, the XEPTable object will be updated
        with the properties of the XEP, otherwise a new XEP is added.

        Arguments:
          xep (xep): the XEP-object to add or update.
        """
        props = (("number", xep.nrFormatted),
                 ("name", xep.title),
                 ("type", xep.type),
                 ("status", xep.status),
                 ("updated", xep.date.date()),
                 ("shortname", xep.shortname),
                 ("abstract", xep.abstract))
        x = self.doc.createElement("xep")
        update = False
        for xepNode in self.doc.getElementsByTagName("xep"):
            if xepNode.getElementsByTagName("number")[0].childNodes[0].data == xep.nrFormatted:
                x = xepNode
                update = True
                break
        if update:
            for prop in props:
                x.getElementsByTagName(prop[0])[0].childNodes[0].data = prop[1]
        else:
            for prop in props:
                p = self.doc.createElement(prop[0])
                if prop[1]:
                    t = self.doc.createTextNode(str(prop[1]))
                else:
                    t = self.doc.createTextNode("")
                p.appendChild(t)
                x.appendChild(p)
            self.doc.childNodes[0].appendChild(x)

    def writeXMLTable(self, filename):
        """
        Outputs the XEP index table in XML format.

        Arguments:
          filename (str): the filename of the file to output to, will be
          overwritten.
        """
        self.doc.getElementsByTagName("xeps")[0].normalize()
        f = open(filename, "wb")
        self.doc.writexml(f)
        f.close()

    def writeHTMLTable(self, filename):
        """
        Outputs the XEP index table in HTML format.

        Arguments:
          filename (str): the filename of the file to output to, will be
          overwritten.
        """
        html = HTMLTableHeader
        for xep in self.doc.getElementsByTagName('xep'):
            atribs = {}
            # assume there is just one child node and that that is a textnode
            for atrib in ("status", "number", "name", "type", "status", "updated"):
                atribs[atrib] = xep.getElementsByTagName(
                    atrib)[0].childNodes[0].data
            html += HTMLTableRow.format(**atribs)
        html += HTMLTableFooter
        f = open(filename, "w")
        f.write(html)
        f.close()

    def __str__(self):
        """
        The raw XML of the xep table.
        """
        return self.doc.toprettyxml()

    def __repr__(self):
        """
        The raw XML of the xep table.
        """
        return self.__str__()
