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
import sys
import traceback

def getText(nodelist):
    """Utility function, reads content of all textnodes into one string"""
    thisText = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            thisText = thisText + node.data
    return thisText

def replaceElementText(filename, elementname, text):
    """Utility function, updates the text of the first occurance of an
       element of a XML file in place.

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
        nr (int or str):                The XEP 'number' as in the header of
                                            the XEP, integer or str if it is
                                            XEP-README or XEP-template
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
        nr = getText((headerNode.getElementsByTagName("number")[0]).childNodes)
        path, fle = os.path.split(self.filename)
        if os.path.basename(path) == 'inbox' or fle == "xep-template.xml":
            # these should have 'xxxx' as number
            if not nr == "xxxx":
                print "Invalid value for XEP-number ({0}) while parsing protoXEP.".format(nr)
                print "  XEP file: {}".format(self.filename)
                print
            self.nr = fle[:-4]
        elif fle == "xep-README.xml" and nr == "README":
            self.nr = nr
        else:
            try:
                self.nr = int(nr)
            except:
                self.nr = nr
                self.__printParsingError__("XEP number")
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
            try:
                self.lastcall = datetime.datetime.strptime(lastcallString,"%Y-%m-%d")
            except:
                self.lastcall = False
                self.__printParsingError__("last call")
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
        try:
            self.date = datetime.datetime.strptime(dateString,"%Y-%m-%d")
        except:
            self.date = datetime.datetime.now()
            self.__printParsingError__("date")
        self.version = getText((revNode.getElementsByTagName("version")[0]).childNodes)
        try:
            self.majorVersion = int(self.version.split('.')[0])
        except:
            self.majorVersion = 0
            self.__printParsingError__("major version")
        try:
            self.minorVersion = int(self.version.split('.')[1])
        except ValueError:
            if self.interim:
                self.minorVersion = self.version.split('.')[1]
            else:
                self.minorVersion = 0
                self.__printParsingError__("major version")
                
        depNode = headerNode.getElementsByTagName("dependencies")
        self.depends = []
        if depNode:
            depNode = depNode[0]
            for dep in depNode.getElementsByTagName("spec"):
                self.depends.append(getText(dep.childNodes))

    def __str__(self):
        """
        The XEP name es string, e.g: 'XEP-0001'
        """
        if not self.nr:
            print self.filename
        if type(self.nr) is int:
            return "XEP-{:0>4d}".format(self.nr)
        else:
            return "XEP-{0}".format(self.nr)

    def __repr__(self):
        """
        The XEP name es string, e.g: 'XEP-0001'
        """
        return self.__str__()

    def __printParsingError__(self, valuedescription):
        """
        Prints a nice message when some value doesn't parse.
        """
        print "Invalid value for {0} while parsing {1}, setting to a default.".format(valuedescription, str(self))
        print "  XEP file: {}".format(self.filename)
        print "  Error: {}".format(sys.exc_info()[1])
        print

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
        """
        Marks XEP as 'Deferred'
        """
        replaceElementText(self.filename, "status", "Deferred")
        self.status = "Deferred"


    def buildXHTML(self):
        """
        Generates a nice formatted XHTML file from the XEP.
        """
        # ToDo
        pass

    def buildPDF(self):
        """
        Generates a nice formatted XHTML file from the XEP.
        """
        # ToDo
        pass
        

class AllXEPs(object):
    """
    Class containing info about all XEP XML files from one directory
    """
    def __init__(self, directory, allFiles=True):
        """
        Reads all XEP XML-files in directory and parses the meta-info.

        Arguments:
            directory (str): Directory to search XEP-files in
            allFiles (bool): When true, all xml in the directory are parsed
                             otherwise only the files with the format:
                             xep-????.xml
        """
        self.xeps = []
        if allFiles:
            fltr = '*.xml'
        else:
            fltr = 'xep-????.xml'
        fltr = os.path.join(os.path.abspath(directory), fltr)
        files = glob.glob(fltr)
        files.sort()
        for fle in files:
            try:
                self.xeps.append(XEP(fle))
            except:
                print "Error while parsing {}".format(fle)
                print "WARNING: XEP is not included"
                print traceback.format_exc()

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
                      defaults to 365 days
        """
        cutOff = datetime.datetime.now()-datetime.timedelta(days=idle)
        return [x for x in self.xeps if x.status == "Experimental" and x.date < cutOff]

    def buildAll(self):
        """
        Generate XHTML and PDF Files for all XEPs, including a XHTML index table
        """
        # ToDo
        pass

    def buildTables(self):
        """
        Generates XHTML and XML index tables of all XEPs
        """
        # ToDo
        pass
