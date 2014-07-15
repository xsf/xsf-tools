# File: repository.py
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

import os
import glob
import subprocess
import tempfile
import traceback
import datetime
import tarfile
import xeputils.xep
import xeputils.xeptable

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
    Class containing info about all XEP XML files from one directory
    """
    def __init__(self, directory, outpath=None, allFiles=False):
        """
        Reads all XEP XML-files in directory and parses the meta-info.

        Arguments:
            directory (str): Directory to search XEP-files in.
            outpath (str):   Directory to place the build XEPs in. Will be
                             created when non-existing. When empty, False or
                             None, a temporary directory will be created.
            allFiles (bool): When true, all xml files in the directory are
                             parsed otherwise only the files with the format:
                             xep-????.xml are parsed.
        """
        self.directory = directory
        self.outpath = prepDir(outpath)
        self.errors = []
        p = subprocess.Popen(["git", "rev-parse", "--show-toplevel"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd=directory)
        (out, error) = p.communicate()
        if error:
            self.gittoplevel = None
        else:
            self.gittoplevel = out.strip()
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
                self.xeps.append(xeputils.xep.XEP(fle, outpath=self.outpath))
            except:
                e = "Error while parsing {}\n".format(fle)
                e += "WARNING: XEP is not included\n"
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
        cutOff = datetime.datetime.now()-datetime.timedelta(days=idle)
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

    def buildAll(self):
        """
        Generate XHTML and PDF Files for all XEPs, including a XHTML index table

        Argumens:
          outpath (str): path to write build files to. A temporary directory
                         will be created when no outpath is provided.
        """
        self.revertInterims()
        for xep in self.xeps:
            xep.buildXHTML(self.outpath)
            xep.buildPDF(self.outpath)
        self.buildTables(
            os.path.join(self.outpath, "xeps.xml"),
            os.path.join(self.outpath, "xeplist.txt"))
        self.buildBundle()

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
        Generates a tar.bz2 file containing all PDF files in the out path of
        this repository. The created tarfile will be:
            [name].tar.bz2

        Arguments:
          name (str):      The name of the tarbal, defaults to 'xepbundle'
        """
        fltr = os.path.join(os.path.abspath(self.outpath), '*.pdf')
        files = glob.glob(fltr)
        files.sort()
        tar = tarfile.open(os.path.join(self.outpath, "{}.tar.bz2".format(name)),
                           "w:bz2")
        for name in files:
            tar.add(name, arcname="xepbundle/{}".format(os.path.basename(name)))
        tar.close()

    def revertInterims(self):
        """
        Reverts the interim XEPs to their last non-interim state.
        """
        if not self.gittoplevel:
            self.errors.append("WARNING: not in a git repository, will be using interim XEPs")
            return
        commitIndex = 1
        while self.getInterim():
            for interim in self.getInterim():
                gitref = os.path.relpath(interim.filename, self.gittoplevel)
                p = subprocess.Popen(["git", "log", "--pretty=format:%H", gitref],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=self.gittoplevel)
                (out, error) = p.communicate()
                if error:
                    interim.buildErrors.append("WARNING: error reading git log, not reversing interim XEP {}: {}".format(str(interim), error))
                else:
                    commits = out.split('\n')
                    p = subprocess.Popen(["git", "show", "{}:{}".format(commits[commitIndex], gitref)],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        cwd=self.gittoplevel)
                    (out, error) = p.communicate()
                    if error:
                        interim.buildErrors.append("WARNING: error reading git blob, not reversing interim XEP {}: {}".format(str(interim), error))
                    else:
                        interim.raw = out
                        interim.readXEP()
            commitIndex += 1

    def printErrors(self):
        """
        prints a overview of errors that occured while parsing and building the XEPs.
        """
        xepsWithErrors = list(set(self.getParseErrors()+self.getBuildErrors()))
        xepsWithErrors.sort()
        if self.getErrors() or xepsWithErrors:
            if self.getErrors():
                print "********** Generic errors **********"
                for error in self.getErrors():
                    print error
            for xep in xepsWithErrors:
                print "********** Error report for {} **********".format(str(xep))
                if xep.parseErrors:
                    print "********** Parsing Errors **********"
                    errors = list(set(xep.parseErrors))
                    for error in errors:
                        print error
                if xep.buildErrors:
                    print "********** Build Errors **********"
                    for error in xep.buildErrors:
                        if len(error.splitlines()) > 4:
                            error = ''.join(error.splitlines()[:4])
                        print error
                        
        else:
            print "No errors"
