#!/usr/bin/env python

# File: testscript.py
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

import sys
import os

# hack to import relative to this script
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import xeputils.repository

# read current repository
a = xeputils.repository.AllXEPs(os.getcwd(), allFiles=True)
if 0:
    print "Interim:"
    print a.getInterim()
    print "No short name:"
    print a.getNoShortName()
    print "Last Call:"
    print a.getLastCall()
    print "Expired:"
    for i in a.getExpired():
        print i, i.date
if 0:
    print "With images:"
    for i in a.getWithImages():
        i.pprint()
        i.buildPDF()
        #i.updateTable("/tmp/all.xml", "/tmp/all.html")
if 0:
    ii = a.getInterim()
    a.revertInterims()
    for i in ii:
        i.buildXHTML()
if 1:
    print "Building all"
    a.buildAll()
    a.printErrors()
