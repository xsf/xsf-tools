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
import tempfile
import traceback
import datetime
import xeputils.xep

def prepDir(path=None):
    """
    Utility function, to prepare a directory for e.g. storing the generated
    XEPs.

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
    print "creating {}".format(path)
    return path

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
                self.xeps.append(xeputils.xep.XEP(fle))
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

    def buildAll(self, outpath=None):
        """
        Generate XHTML and PDF Files for all XEPs, including a XHTML index table
        """
        outpath = prepDir(outpath)
        for xep in self.xeps:
            xep.buildXHTML(outpath)
            xep.buildPDF(outpath)
        # ToDo: table

    def buildTables(self):
        """
        Generates XHTML and XML index tables of all XEPs
        """
        # ToDo
        pass

# ToDo: get previous version of interim XEP
