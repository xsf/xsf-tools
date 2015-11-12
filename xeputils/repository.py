# File: repository.py
# Version: 0.3
# Description: utility functions for handling XEPs
# Last Modified: 2014-09-23
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

import os
import sys
import glob
import tempfile
import traceback
import datetime
import tarfile
import xeputils.xep
import xeputils.xeptable
import xeputils.mail


def prepDir(path=None):
    """
    Utility function, to prepare a directory for e.g. storing the generated
    XEPs. Returns the outpath in use.

    Arguments:
      path (str):  The path to prepare, when empty, False or None, a temporary
                   directory will be created.
    """
    if path:
        if os.path.exists(path):
            return path
        else:
            os.makedirs(path)
    else:
        # Do something innocent when no path is provided
        path = tempfile.mkdtemp(prefix='XEPs_')
    print "creating {} for output".format(path)
    return path


class AllXEPs(object):

    """
    Class containing info about all XEP XML files specified when instantiating.
    """

    def __init__(self, config):
        """
        Reads all XEP XML-files in directory and parses the meta-info.

        Arguments:
            xeps (list):     XEPs to parse, each item can either be a filename,
                             a directory or a XEP-number. If a directory is
                             given, all xml files in that directory are
                             processed. If a number is given (in the format of
                             '0001') then it looks for the xml source of that
                             XEP in the current directory.
                             If the list is empty or omitted, it tries to parse
                             all xml files in the current working directory.
            outpath (str):   Directory to place the build XEPs in. Will be
                             created when non-existing. When empty, False or
                             None, a temporary directory will be created.
            xslpath (str):   Directory to look for the XSLT stylesheets and the
                             other build depencies. A sensible guess based on
                             the XEPs location is made when not suppied.
        """
        self.config = config
        self.outpath = prepDir(config.outpath)
        self.xslpath = config.xslpath
        self.errors = []
        self.xeps = []
        files = []
        if config.xeps:
            for xep in config.xeps:
                if os.path.isfile(xep):
                    files.append(os.path.abspath(xep))
                elif os.path.isdir(xep):
                    fltr = os.path.join(os.path.abspath(xep), '*.xml')
                    files += glob.glob(fltr)
                else:
                    if os.path.isfile("xep-{0}.xml".format(xep)):
                        files.append(
                            os.path.abspath(os.path.join(os.getcwd(), "xep-{0}.xml".format(xep))))
        else:
            # no xeps given, try all xml-files in curdir
            fls = glob.glob(os.path.join(os.getcwd(), '*.xml'))
            for fle in fls:
                files.append(os.path.abspath(fle))
        # try if we can find an existing XEP-table:
        if os.path.isfile(os.path.join(self.outpath, "xeps.xml")):
            self.xeptable = os.path.join(self.outpath, "xeps.xml")
        else:
            self.xeptable = None
        # read files to xeps
        for fle in sorted(set(files)):
            try:
                self.xeps.append(
                    xeputils.xep.XEP(fle,
     outpath=self.outpath,
     xslpath=self.xslpath))
            except:
                e = "Error while parsing {}\n".format(fle)
                e += "FATAL: {} is not included\n".format(fle)
                e += traceback.format_exc()
                self.errors.append(e)

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

    def getWithImages(self):
        """
        Returns list with XEP objects of all XEPs that have img tags.
        Mainly for testing purposes.
        """
        return [x for x in self.xeps if x.images]

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
        cutOff = datetime.datetime.now() - datetime.timedelta(days=idle)
        return [x for x in self.xeps if x.status == "Experimental" and x.date < cutOff]

    def getErrors(self):
        """
        Returns list with generic errors while processing the repository
        """
        return self.errors

    def getBuildErrors(self):
        """
        Returns list with XEP objects that met errors while building
        """
        return [x for x in self.xeps if x.buildErrors]

    def getParseErrors(self):
        """
        Returns list with XEP objects that met errors while parsing
        """
        return [x for x in self.xeps if x.parseErrors]

    def buildAll(self, showprogress=False):
        """
        Generate XHTML and PDF Files for all XEPs, including a XHTML index
        table and a tarred bundle of generated PDF's.
        Reverts interims before building.
        """
        if showprogress:
            sys.stdout.write("\rReverting interm XEPs")
            sys.stdout.flush()
            counter = 1
        self.revertInterims()
        for xep in sorted(self.xeps):
            if showprogress:
                sys.stdout.write("\rBuilding XEP: ... {:<40}  [{}/{}]".format(
                    xep.filename[-40:], counter, len(self.xeps)))
                sys.stdout.flush()
                counter += 1
            xep.buildXHTML(self.outpath, self.xslpath)
            xep.buildPDF(self.outpath, self.xslpath)
        if showprogress:
            sys.stdout.write("\rBuilding index table")
            sys.stdout.flush()
        self.buildTables(
            os.path.join(self.outpath, "xeps.xml"),
            os.path.join(self.outpath, "xeplist.txt"))
        self.buildBundle()
        if showprogress:
            sys.stdout.write("\rDone!\n")
            sys.stdout.flush()

    def buildTables(self, xmlfile, htmlfile):
        """
        Generates HTML and XML index tables of all XEPs, overwriting the
        previous tables.

        Arguments:
          xmlfile (str):  filename of the file to write the XML table to.
          htmlfile (str): filename of the file to write the HTML table to.
        """
        t = xeputils.xeptable.XEPTable()
        for xep in self.xeps:
            t.updateXEP(xep)
        t.writeXMLTable(xmlfile)
        t.writeHTMLTable(htmlfile)

    def updateHTMLTable(self, xmlfile, htmlfile):
        """
        Uses a cached XML XEP table to generate an updated HTML XEP table.

        Arguments:
          xmlfile (str):  filename of the existing XML file.
          htmlfile (str): filename of the file to write the HTML table to.
        """
        t = xeputils.xeptable.XEPTable(xmlfile)
        t.writeHTMLTable(htmlfile)

    def buildBundle(self, name="xepbundle"):
        """
        Generates a tar.bz2 file containing all PDF files in the outpath of
        this repository. The created tarfile will be:
            [name].tar.bz2

        Arguments:
          name (str):      The name of the tarbal, defaults to 'xepbundle'
        """
        fltr = os.path.join(os.path.abspath(self.outpath), '*.pdf')
        files = sorted(glob.glob(fltr))
        tar = tarfile.open(
            os.path.join(self.outpath, "{}.tar.bz2".format(name)),
            "w:bz2")
        for name in files:
            tar.add(
                name, arcname="xepbundle/{}".format(os.path.basename(name)))
        tar.close()

    def revertInterims(self):
        """
        Reverts the interim XEPs to their last non-interim state.
        """
        for interim in self.getInterim():
            interim.revertInterim()

    def processErrors(self):
        """
        Prints an overview of errors that occured while parsing and building the
        XEPs.
        """
        e = self.formatErrors()
        if not self.config.nologtostdout:
            if e:
                print e
            else:
                print "No errors"
        if self.config.logtomail:
            if e:
                m = xeputils.mail.LogMail(self.config, e)
                m.send()
        if self.config.logtofile:
            f = open(self.config.logtofile, 'a')
            f.write("\n===================\n")
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            f.write("\n===================\n")
            if e:
                f.write(e)
            else:
                f.write("No errors")
            f.close()

    def formatErrors(self):
        """
        If there were any during the parsing or the building of the XEPs, it
        returns a string with a nicely formatted list of errors, suitable for
        printing or including in a mail. Returns None if there weren't any
        errors (either because parsing and building went perfect or because
        there were no XEPs parsed or build yet).
        """
        errorlist = []
        xepsWithErrors = sorted(
            set(self.getParseErrors() + self.getBuildErrors()),
            key=lambda x: str(x))
        if self.getErrors() or xepsWithErrors:
            if self.getErrors():
                errorlist.append("********** Read errors **********")
                for error in self.getErrors():
                    errorlist.append(error)
            for xep in xepsWithErrors:
                errorlist.append(
                    "********** Error report for {} **********".format(str(xep)))
                if xep.parseErrors:
                    errorlist.append("********** Parsing Errors **********")
                    errors = list(set(xep.parseErrors))
                    for error in errors:
                        errorlist.append(error)
                if xep.buildErrors:
                    errorlist.append("********** Build Errors **********")
                    for error in xep.buildErrors:
                        if len(error.splitlines()) > 4:
                            error = ''.join(error.splitlines()[:4])
                        errorlist.append(error)
            return '\n'.join(errorlist)
        else:
            return None
