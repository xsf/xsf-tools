# File: xeputils.py
# Version: 0.1
# Description: utility functions for handling XEPs
# Last Modified: 2014-06-03
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

from xml.dom.minidom import parse,parseString,Document,getDOMImplementation
import datetime
import glob
import os
import re
import traceback

def getText(nodelist):
    """Reads content of all textnodes into one string"""
    thisText = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            thisText = thisText + node.data
    return thisText

def replaceElementText(filename, elementname, text):
    """Updates the text of the first occurance of an element of a XML file in
       place.

       Arguments:
           filename (str):      Name of the XML file to modify
           elementname (str):   Name of the element to modify
           text (str):          Text to replace the text of the elemen with
    """
    # EVIL HACK WARNING:
    # Using a XMP parser to read and write the XEP more or less destroys it, so
    # we use blunt text replacement to update the element.
    f = open(filename, 'r')
    xepText = f.read()
    f.close()
    pattern = "<{0}>[a-zA-Z0-9]*</{0}>".format(elementname)
    replacement = "<{0}>{1}</{0}>".format(elementname, text)
    xepText = re.sub(pattern, replacement, xepText, count=1)
    f = open(filename, 'w')
    f.write(xepText)
    f.close()

class XEP(object):
    """
    Class describing a XEP, as parsed from its XML
    
    Attributes:
        abstract (str):                 The XEP 'abstract'
        date (datetime):                The date of the latest revision of
                                            the XEP
        depends (list):                 List of strings containing all specs
                                            listed in this XEP dependencies
                                            nodes
        filename (str or None)          Full filename of the parsed XEP, None if
                                            the XEP was parsed from a raw XML
                                            string
        interim (bool):                 True if the XEP has an 'interim' tag
        lastcall (datetime or False):   The 'lastcall' date, if the XEP has
                                            one, else False
        majorVersion (int):             The first digit of the the version
                                            string
        minorVersion (int or str):      The second digit of the version
                                            string, will be string if it is a
                                            interim XEP release candidate
        nr (int):                       The XEP 'number' as in the header of
                                            the XEP
        shortname (str or None):        The 'shortname', if the XEP has one,
                                            else None
        status (str):                   The 'status' of the XEP
        title (str):                    The XEP 'title'
        type (str):                     The 'type' of the XEP
        version (str):                  The full version string of the
                                            latest revision of the XEP
        xep (minidom document)          The full XML tree of the XEP as minidom
                                            document
    """

    def __init__(self, filename_or_xml, parseStr=False):
        """
        Creates an XEP object.

        Arguments:
            filename_or_xml (str):  The filename of the XEP to be read or the
                                        raw XML of the XEP
            parseStr (bool):        Optional, when true, the first argument is parsed as
                                        raw XML
        """
        if parseStr:
            thexep = parseString(filename_or_xml)
            self.filename = None
        else:
            thexep = parse(filename_or_xml)
            self.filename = filename_or_xml
        self.xep = thexep
        xepNode = (thexep.getElementsByTagName("xep")[0])
        headerNode = (xepNode.getElementsByTagName("header")[0])
        titleNode = (headerNode.getElementsByTagName("title")[0])
        self.title = getText(titleNode.childNodes)
        self.nr = int(getText((headerNode.getElementsByTagName("number")[0]).childNodes))
        shortnameNode = headerNode.getElementsByTagName("shortname")
        if shortnameNode:
            self.shortname = getText((shortnameNode[0]).childNodes)
        else:
            self.shortname = None
        abstractNode = (headerNode.getElementsByTagName("abstract")[0])
        self.abstract = getText(abstractNode.childNodes)
        statusNode = (headerNode.getElementsByTagName("status")[0])
        self.status = getText(statusNode.childNodes)
        lastcallNode = (headerNode.getElementsByTagName("lastcall"))
        if lastcallNode:
            lastcallNode = lastcallNode[0]
            lastcallString = getText(lastcallNode.childNodes)
            self.lastcall = datetime.datetime.strptime(lastcallString,"%Y-%m-%d")
        else:
            self.lastcall = False
        self.type = getText((headerNode.getElementsByTagName("type")[0]).childNodes)
        titleNode = (headerNode.getElementsByTagName("interim"))
        if titleNode:
            self.interim = True;
        else:
            self.interim = False;
        revNode = (headerNode.getElementsByTagName("revision")[0])
        dateString = getText((revNode.getElementsByTagName("date")[0]).childNodes)
        self.date = datetime.datetime.strptime(dateString,"%Y-%m-%d")
        self.version = getText((revNode.getElementsByTagName("version")[0]).childNodes)
        self.majorVersion = int(self.version.split('.')[0])
        try:
            self.minorVersion = int(self.version.split('.')[1])
        except ValueError:
            if self.interim:
                self.minorVersion = self.version.split('.')[1]
            else:
                raise

        depNode = headerNode.getElementsByTagName("dependencies")
        self.depends = []
        if depNode:
            depNode = depNode[0]
            for dep in depNode.getElementsByTagName("spec"):
                self.depends.append(getText(dep.childNodes))

    def __str__(self):
        return "XEP-{:0>4d}".format(self.nr)

    def __repr__(self):
        return self.__str__()

    def pprint(self):
        """
        Prints a nice overview of the parsed info of the XEP.
        """
        items = self.__dict__.keys()
        items.remove('xep') # no need for this one
        items.sort(reverse=True) # hack to get a nicer order
        print self.__str__()
        for item in items:
            print "  {:<18}  {}".format(item, self.__dict__[item])

    def setDeferred(self):
        replaceElementText(self.filename, "status", "Deferred")
        self.status = "Deferred"

class AllXEPs(object):
    """
    Class containing info about all XEP XML files from one directory
    """
    def __init__(self, directory):
        """
        Reads all XEP XML-files in directory and parses the meta-info.

        Arguments:
            directory (str): directory to search XEP-files in
        """
        self.xeps = []
        files = glob.glob(os.path.abspath(directory)+'/xep-????.xml')
        files.sort()
        for fle in files:
            try:
                self.xeps.append(XEP(fle))
            except:
                print "Error while parsing {}".format(fle)
                traceback.print_exc()

    def getInterim(self):
        """
        Returns list with XEP objects of all XEPs with the status 'interim'.
        """
        return [x for x in self.xeps if x.interim]

    def getNoShortName(self):
        """
        Returns list with XEP objects of all XEPs without a shortname.
        Mainly for testing purposes.
        """
        return [x for x in self.xeps if not x.shortname]
        
    def getLastCall(self):
        """
        Returns list with XEP objects of all XEPs that have a last call.
        """
        return [x for x in self.xeps if x.lastcall]

    def getExpired(self, idle=365):
        """
        Returns list with XEP objects of all experimental XEPs that have
        been idle for more then 'idle' days.

        Arguments:
          idle (int): optional number of days before an experimental XEP expires
        """
        cutOff = datetime.datetime.now()-datetime.timedelta(days=idle)
        return [x for x in self.xeps if x.status == "Experimental" and x.date < cutOff]
