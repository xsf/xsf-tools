#!/usr/bin/env python

# File: config.py
# Version: 0.1
# Description: utility functions for handling XEPs
# Last Modified: 2014-07-18
# Based on scripts by:
#    Tobias Markmann (tm@ayena.de)
#    Peter Saint-Andre (stpeter@jabber.org)
# Authors:
#    Winfried Tilanus (winfried@tilanus.com)

# LICENSE ##
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
# END LICENSE ##

#!/usr/bin/env python
import imp
import os
import sys
import argparse


class Config(object):

    """
    Configuration object.

    The configuration is read from the command line arguments. When not supplied,
    values in the configfile are used. When a value is not read from the config
    file, the default as defined in _defaults is used.

    The configurations are accessible as properties of the instance. EG:
        >> config = xeputils.config.Config()
        >> print config.confile
        config.py

    The configfile has to be a python file in the form:

    -----
    # config for this server
    options = {
        "property1": "value1",
        "property2": True,
        "property3" = 3
        }
    -----

    The configfile will be read from the location specified with the --conffile
    or -c command line option. If no full path is provided, it will look
    relative to the current working directory. When no conffile is provided on the
    commandline, it will look for "config.py" in the current working directory.

    Fixed Class Properties:
      _defaults (dict):         A dictionary containing the defaults.
      _parser (ArgumentParser): The parser object (from the argparse module)
      _argdict (dict):          A dictionary containing the parsed configuration

    If you want to add a commandline option to a script, use:
        config = xeputils.config.Config(parse=False)
        config._parser.add_argument("-t", "--toast", action="store_true",
                                    help="Make toast")
        config._parse()
    See the argparse documentation for the add_argument method.
    """
    _defaults = {
        "conffile": "config.py",
        "logtostdout": True,
        "mailserver": "localhost",
    }

    def __init__(self, parse=True):
        """
        Creates a new configuration object.

        arguments:
          process (bool):   When False, it won't parse the arguments, so
                            arguments additional to the default options can be
                            added to the ._parser object. Afterwards to that
                            the ._parse method needs to be called.
        """
        # add help later, then all options are included
        self._parser = argparse.ArgumentParser(add_help=False)
        self._parser.add_argument("-c", "--conffile",
                                  help="Specify config file.", metavar="FILE")
        self._argdict = vars(self._parser.parse_known_args()[0])
        if not self.conffile:
            # set configfile when not provided on commandline
            self._argdict["conffile"] = self._defaults["conffile"]
        elif not os.path.isfile(self.conffile):
            # don't raise when no file provided on commandline
            raise IOError("Configuration file not found")
        self._parser.set_defaults(**self._defaults)
        if os.path.isfile(self.conffile):
            conffile = imp.load_source("conffile", self.conffile)
            self._parser.set_defaults(**conffile.options)
        self._setStandardOptions()
        if parse:
            self._parse()

    def __getattribute__(self, name):
        """
        Wrapper, so we can refer configs like: config.property1. Skip when the
        name starts with "_", to avoid endless recursion....
        """
        if not name[0] == "_":
            if name in self._argdict.keys():
                return self._argdict[name]
        return object.__getattribute__(self, name)

    def _setStandardOptions(self):
        """
        Ads standard options:
        --help / -h
        --debug / -d
        --sendmail / -s
        --mailto [E-MAIL ADDRESS] / -t [E-MAIL ADDRESS]
        --mailfrom [E-MAIL ADDRESS] / -f [E-MAIL ADDRESS]
        --logtofile [FILE] / -l [FILE]
        --logtostdout
        --logtomail
        --mailserver [SERVER]
        --xeps / -x
        --outpath / -o
        --xslpath
        """
        self._parser.add_argument("-h", "--help", action='store_true',
                                  help="Print this help.")
        self._parser.add_argument("-d", "--debug", action='store_true',
                                  help="Print debugging output to stdout while processing")
        self._parser.add_argument("-s", "--sendmail", action='store_true',
                                  help="Send notification mails. If no --mailto is given, print mails to stdout")
        self._parser.add_argument("--nologtostdout", action='store_true',
                                  help="Suppress printing logging messages to stdout")
        self._parser.add_argument("--logtomail", action='store_true',
                                  help="Send logging messages by mail to --mailto adresses")
        self._parser.add_argument("-l", "--logtofile", metavar="FILE",
                                  help="Specify file to send logs to.")
        self._parser.add_argument("-t", "--mailto", metavar="E-MAIL ADDRESS",
                                  help="Specify e-mail address to send mails to.")
        self._parser.add_argument("-f", "--mailfrom", metavar="E-MAIL ADDRESS",
                                  help="Specify from mail address.")
        self._parser.add_argument("--mailserver", metavar="SERVER",
                                  help="Specify e-mail addresses to send mails to.")
        self._parser.add_argument("-x", "--xeps", metavar="XEP", nargs="+",
                                  help="XEPs to parse, each item can either be a filename, a directory or a XEP-number. If a directory is given, all xml files in that directory are processed. If a number is given                                  (in the format of '0001') then it looks for the xml source of that XEP in the current directory. When not given it tries to parse all xml files in the current working directory.")
        self._parser.add_argument("-o", "--outdir", metavar="PATH",
                                  help="Specify directory for build results. Will be created when not existent. A temporary directory will be used when not specified.")
        self._parser.add_argument("--xslpath", metavar="PATH",
                                  help="Specify path where to look for the XSL stylesheets and the other build dependencies when building the XEP.")

    def _parse(self):
        """
        Parses the commandline options.
        """
        self._argdict = vars(self._parser.parse_args())
        if self.help:
            self._parser.print_help()
            sys.exit(1)
