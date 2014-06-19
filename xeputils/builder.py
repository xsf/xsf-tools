# File: builder.py
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
import shutil
import tempfile
import subprocess
import xeputils.repository

def buildXHTML(self, outpath=None):
    """
    Generates a nice formatted XHTML file from the XEP.

    Arguments:
      path (str): The full path were the tree of the generated XEPs should
                  be build. When unspecified, a temporary directory
                  directory in systems default temporary file location is
                  used.
    """
    outpath = xeputils.repository.prepDir(outpath)
    if os.path.basename(self.path) == 'inbox':
        inbox = True
        xslpath = os.path.abspath(os.path.join(self.path, ".."))
        # hack to make sure xep.ent & xep.dtd is in the correct dir
        shutil.copy(os.path.join(xslpath, "xep.ent"), self.path)
        shutil.copy(os.path.join(xslpath, "xep.dtd"), self.path)
    else:
        inbox = False
        xslpath = self.path

    # Overloading is great, but sometimes a burden ;-)
    if type(self.nr) is int:
        nr = "{:0>4d}".format(self.nr)
    else:
        nr = "{}".format(self.nr)

    # XHTML
    outfile = open(os.path.join(outpath, "xep-{}.html".format(nr)), "w")
    xsl = os.path.join(xslpath, "xep.xsl")
    p = subprocess.Popen(["xsltproc", xsl, self.filename],
                          stdout=outfile,
                          stderr=subprocess.PIPE)
    (dummy, error) = p.communicate()
    outfile.close()
    if error:
        print "Error while generating XHTML for {0}: {1}".format(str(self), error)

    # Reference
    if not os.path.exists(os.path.join(outpath, "refs")):
        os.makedirs(os.path.join(outpath, "refs"))
    outfile = open(os.path.join(outpath, "refs", "reference.XSF.XEP-{}.xml".format(nr)), "w")
    xsl = os.path.join(xslpath, "ref.xsl")
    p = subprocess.Popen(["xsltproc", xsl, self.filename],
                          stdout=outfile,
                          stderr=subprocess.PIPE)
    (dummy, error) = p.communicate()
    outfile.close()
    if error:
        print "Error while generating reference for {0}: {1}".format(str(self), error)

    # Examples
    if not os.path.exists(os.path.join(outpath, "examples")):
        os.makedirs(os.path.join(outpath, "examples"))
    outfile = open(os.path.join(outpath, "examples", "{}.xml".format(nr)), "w")
    xsl = os.path.join(xslpath, "examples.xsl")
    p = subprocess.Popen(["xsltproc", xsl, self.filename],
                          stdout=outfile,
                          stderr=subprocess.PIPE)
    (dummy, error) = p.communicate()
    outfile.close()
    if error:
        print "Error while generating examples for {0}: {1}".format(str(self), error)

    # The source xml
    shutil.copy(self.filename, outpath)

    # Cleanup
    if inbox:
        os.remove(os.path.join(self.path, "xep.ent"))
        os.remove(os.path.join(self.path, "xep.dtd"))

def buildPDF(self, outpath=None):
    """
    Generates a nice formatted PDF file from the XEP.


    Arguments:
      path (str): The full path were the tree of the generated XEPs should
                  be build. When unspecified, a temporary directory
                  directory in systems default temporary file location is
                  used.
    """
    # ToDo
    pass
