# File: mail.py
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

import smtplib
import sys
import datetime


class BaseMessage(object):

    """Class to be subclassed for sending messages. When sublassing the variable
       "MESSAGETEXT" has to be overwritten. Optionally the method "makeSubject"
       can be overwritten.

       Class properties:
       MESSAGETEXT (str):     String containing the message, including the
                              headers. Python string formatting as defined in:
                              https://docs.python.org/2/library/string.html#format-string-syntax
                              can be used in it. The 'config' and 'xep' objects
                              will be available when formatting as well as the
                              string 'subject' (as set by the 'makeSubject'
                              method').
       xep (xep object):      The XEP (object) to send the message about.
       config (config object: The config (object) when composing and sending
                              the message."""
    MESSAGETEXT = """From: {config.mailfrom}
To: {config.mailto}
Subject: {subject}

This is a testmessage about XEP-{xep.nrFormatted} ({xep.title}), please
ignore.
"""

    def __init__(self, config, xep):
        """Create a new message.
           Arguments:
           config (config object): The config (object) to use.
           xep (xep object):       The XEP (object) this message is about."""
        self.config = config
        self.xep = xep

    def makeSubject(self):
        """Class to be overwritten, must return a string containing the
           subject of the message. Can be kept at its default when the string
           'subject' is not used in MESSAGETEXT"""
        return "Testmessage about XEP-{xep.nrFormatted}, ignore.".format(xep=self.xep)

    def send(self, subject=""):
        """Formats and sends the message"""
        subject = self.makeSubject()
        msg = self.MESSAGETEXT.format(
            config=self.config,
            xep=self.xep,
            subject=subject)
        server = smtplib.SMTP(self.config.mailserver)
        server.sendmail(self.config.mailfrom, self.config.mailto, msg)
        server.quit()


class LogMail():
    MESSAGETEXT = """From: {config.mailfrom}
To: {config.mailto}
Subject: There where errors during the run of {script} on {date}

{logs}
"""

    def __init__(self, config, logs):
        self.config = config
        self.logs = logs

    def send(self):
        msg = self.MESSAGETEXT.format(
            config=self.config,
            script=sys.argv[0],
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            logs=self.logs)
        server = smtplib.SMTP(self.config.mailserver)
        server.sendmail(self.config.mailfrom, self.config.mailto, msg)
        server.quit()


class Deferred(BaseMessage):
    MESSAGETEXT = """From: XMPP Extensions Editor <{config.mailfrom}>
To: {config.mailto}
Subject: DEFERRED: XEP-{xep.nrFormatted} ({xep.title})

XEP-{xep.nrFormatted} ({xep.title}) has been Deferred because of inactivity.

Abstract: {xep.abstract}

URL: http://xmpp.org/extensions/xep-{xep.nrFormatted}.html

If and when a new revision of this XEP is published, its status will be changed back to Experimental.
"""
