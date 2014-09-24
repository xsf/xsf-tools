#!/usr/bin/env python

# File: cronjob.py
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

"""
Periodical tasks for maintaining XEPs.
"""

import sys
import os

try:
    import xeputils
except ImportError:
    # hack to import relative to this script, but don't mess with
    # the path when nog needed
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import xeputils

config = xeputils.config.Config()

# read the XEPs
xeps = xeputils.repository.AllXEPs(config)

# Defer expired XEPs
for x in xeps.getExpired():
    x.defer()
    if config.sendmail:
        m = xeputils.mail.Deferred(config, x)
        m.send()
    if xeps.xeptable:
        x.updateTable(xeps.xeptable,
                      os.path.join(xeps.outpath, "xeplist.txt"))

# Make sure we report errors properly
xeps.processErrors()
