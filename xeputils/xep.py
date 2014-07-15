# File: xep.py
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

from xml.dom.minidom import parse,parseString,Document,getDOMImplementation
import sys
import os
import re
import datetime
import xeputils.builder

class XEP(object):
    """
    Class describing a XEP, as parsed from its XML
    
    Attributes:
        abstract (str):                 The XEP 'abstract'
        buildErrors (list):             A list of errors that occured while
                                            building the XEP.
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
                                            XEP-README or XEP-template.
                                            Contains the filename if the XEP is
                                            in the inbox.
        nrFormatted (str):              The XEP 'number' in the format '0001' or
                                            the string value of 'nr'.
        outpath (str or Nont):          The path where build XEPs are stored,
                                            when None, a temporary path is used.
        parseErrors (list):             A list of errors that occured while
                                            parsing the XEP.
        raw (str):                      The raw XML of the XEP as string.
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

    def __init__(self, filename, outpath=None):
        """
        Creates an XEP object.

        Arguments:
            filename (str):  The filename of the XEP to be read.
            outpath (str):   Optional, path to save build XEPs in.
        """
        self.filename = os.path.abspath(filename)
        f = open(self.filename, 'r')
        self.raw = f.read()
        f.close()
        self.outpath = outpath
        self.buildErrors=[]
        self.parseErrors=[]
        self.readXEP()

    def readXEP(self):
        """
        Parses the raw data for further processing.
        """
        self.xep = parseString(self.raw)
        xepNode = (self.xep.getElementsByTagName("xep")[0])
        headerNode = (xepNode.getElementsByTagName("header")[0])
        titleNode = (headerNode.getElementsByTagName("title")[0])
        self.title = self.__getText__(titleNode.childNodes)
        nr = self.__getText__((headerNode.getElementsByTagName("number")[0]).childNodes)
        self.path, fle = os.path.split(self.filename)
        if os.path.basename(self.path) == 'inbox' or fle == "xep-template.xml":
            # these should have 'xxxx' as number
            if not (nr == "xxxx" or nr == "XXXX"):
                e = "Invalid value for XEP-number ({0}) while parsing protoXEP.\n".format(nr)
                e += "  XEP file: {}".format(self.filename)
                self.parseErrors.append(e)
            self.nr = fle[:-4]
        elif fle == "xep-README.xml" and nr == "README":
            self.nr = nr
        else:
            try:
                self.nr = int(nr)
            except:
                self.nr = nr
                self.__processParsingError__("XEP number")
        if isinstance(self.nr, int):
            self.nrFormatted = "{:0>4d}".format(self.nr)
        else:
            self.nrFormatted = self.nr
        shortnameNode = headerNode.getElementsByTagName("shortname")
        if shortnameNode:
            self.shortname = self.__getText__((shortnameNode[0]).childNodes)
        else:
            self.shortname = None
        abstractNode = (headerNode.getElementsByTagName("abstract")[0])
        self.abstract = self.__getText__(abstractNode.childNodes)
        statusNode = (headerNode.getElementsByTagName("status")[0])
        self.status = self.__getText__(statusNode.childNodes)
        lastcallNode = (headerNode.getElementsByTagName("lastcall"))
        if lastcallNode:
            lastcallNode = lastcallNode[0]
            lastcallString = self.__getText__(lastcallNode.childNodes)
            try:
                self.lastcall = datetime.datetime.strptime(lastcallString,"%Y-%m-%d")
            except:
                self.lastcall = False
                self.__processParsingError__("last call")
        else:
            self.lastcall = False
        self.type = self.__getText__((headerNode.getElementsByTagName("type")[0]).childNodes)
        titleNode = (headerNode.getElementsByTagName("interim"))
        if titleNode:
            self.interim = True;
        else:
            self.interim = False;
        revNode = (headerNode.getElementsByTagName("revision")[0])
        dateString = self.__getText__((revNode.getElementsByTagName("date")[0]).childNodes)
        try:
            self.date = datetime.datetime.strptime(dateString,"%Y-%m-%d")
        except:
            self.date = datetime.datetime.now()
            self.__processParsingError__("date")
        self.version = self.__getText__((revNode.getElementsByTagName("version")[0]).childNodes)
        try:
            self.majorVersion = int(self.version.split('.')[0])
        except:
            self.majorVersion = 0
            self.__processParsingError__("major version")
        try:
            self.minorVersion = int(self.version.split('.')[1])
        except ValueError:
            if self.interim:
                self.minorVersion = self.version.split('.')[1]
            else:
                self.minorVersion = 0
                self.__processParsingError__("major version")
                
        depNode = headerNode.getElementsByTagName("dependencies")
        self.depends = []
        if depNode:
            depNode = depNode[0]
            for dep in depNode.getElementsByTagName("spec"):
                self.depends.append(self.__getText__(dep.childNodes))

        imgs = xepNode.getElementsByTagName('img')
        self.images=[]
        for img in imgs:
            self.images.append(img.attributes["src"].value)

    def __str__(self):
        """
        The XEP name as string, e.g: 'XEP-0001'
        """
        if not self.nrFormatted:
            return self.filename
        return "XEP-{0}".format(self.nrFormatted)

    def __repr__(self):
        """
        The XEP name as string, e.g: 'XEP-0001'
        """
        return self.__str__()

    def __processParsingError__(self, valuedescription):
        """
        Utility function, keeps track of of values that didn't parse ok.
        """
        e = "Invalid value for {0} while parsing {1}, setting to a default.\n".format(valuedescription, str(self))
        e += "  XEP file: {}\n".format(self.filename)
        e += "  Error: {}\n".format(sys.exc_info()[1])
        self.parseErrors.append(e)

    def __getText__(self, nodelist):
        """Utility function, reads content of all textnodes into one string"""
        thisText = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                thisText = thisText + node.data
        return thisText

    def replaceElementText(self, elementname, text):
        """Utility function, updates the text of the first occurance of an
           element of a XML file in place.

           Arguments:
               filename (str):      Name of the XML file to modify
               elementname (str):   Name of the element to modify
               text (str):          Text to replace the text of the elemen with
        """
        # EVIL HACK WARNING:
        # Using a XMP parser to read and write the XEP more or less destroys it,
        # so we use blunt text replacement to update the element.
        f = open(self.filename, 'r')
        xepText = f.read()
        f.close()
        pattern = "<{0}>[a-zA-Z0-9]*</{0}>".format(elementname)
        replacement = "<{0}>{1}</{0}>".format(elementname, text)
        xepText = re.sub(pattern, replacement, xepText, count=1)
        f = open(self.filename, 'w')
        f.write(xepText)
        f.close()

    def pprint(self):
        """
        Prints a nice overview of the parsed info of the XEP.
        """
        items = self.__dict__.keys()
        items.remove('xep') # no need for this one
        items.remove('raw') # no need for this one
        items.sort(reverse=True) # hack to get a nicer order
        print self.__str__()
        for item in items:
            if item == "images":
                imgs = []
                for img in self.__dict__[item]:
                    if img[:10] == "data:image":
                        (imgmeta, imgdata) = img.split(',', 1)
                        imgs.append("{0} ({1} bytes)".format(imgmeta, len(imgdata)))
                    else:
                        imgs.append(img)
                print "  {:<18}  {}".format(item, imgs)
            else:
                print "  {:<18}  {}".format(item, self.__dict__[item])

    def setDeferred(self):
        """
        Marks XEP as 'Deferred'
        """
        replaceElementText(self.filename, "status", "Deferred")
        self.status = "Deferred"

    def buildXHTML(self, outpath=None, xslpath=None):
        """
        Generates a nice formatted XHTML file from the XEP.

        Arguments:
          path (str):       The full path were the tree of the generated XEPs should
                            be build. When unspecified, a temporary directory in the
                            systems default temporary file location is used.
          xslpath (str):    The path where the xsl stylesheets can be found. When
                            not specified a directory based on the xep file location
                            is guessed.
        """
        if not outpath and self.outpath:
            outpath=self.outpath
        xeputils.builder.buildXHTML(self, outpath, xslpath)

    def buildPDF(self, outpath=None, xslpath=None):
        """
        Generates a nice formatted PDF file from the XEP.

        Arguments:
          path (str):       The full path were the tree of the generated XEPs should
                            be build. When unspecified, a temporary directory in the
                            systems default temporary file location is used.
          xslpath (str):    The path where the xsl stylesheets can be found. When
                            not specified a directory based on the xep file location
                            is guessed.
        """
        if not outpath and self.outpath:
            outpath=self.outpath
        xeputils.builder.buildPDF(self, outpath, xslpath)

    def updateTable(self, xmlfile, htmlfile):
        """
        Updates the HTML and XML index tables with the properties of this XEP.
        Needs an already existing XML index. Overwrites the previous tables.

        Arguments:
          xmlfile (str):  filename of the XML table to be uptdated.
          htmlfile (str): filename of the HTML table to be updated.
        """
        t = xeputils.xeptable.XEPTable(xmlfile)
        t.updateXEP(self)
        t.writeXMLTable(xmlfile)
        t.writeHTMLTable(htmlfile)
