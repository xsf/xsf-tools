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

"""
Functions for building XHTML and PDF files from XEPs. These have some
dependencies:
 xsltproc (executable binary, debian package xsltproc)
 texml (python module, for source see: http://getfo.org)
 xelatex (executable binary, debian package texlive-xetex)
   Aditionally xelatex needs some dependencies:
        texlive-base (debian package)
        texlive-xetex (debian package)
    	texlive-fonts-extra (debian package)
    	texlive-fonts-recommended (debian package)
        texlive-latex-base (debian package)
    	texlive-latex-extra (debian package)
    	texlive-latex-recommended (debian package)
    	tipa (debian package)
"""

import os
import StringIO
import shutil
import tempfile
import subprocess
import base64
import urlparse
import urllib
import re
import Texml.processor
import xeputils.repository


def buildXHTML(xep, outpath=None, xslpath=None):
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
    outpath = xeputils.repository.prepDir(outpath)
    temppath = tempfile.mkdtemp(prefix='XEPbuilder_')
    if not xslpath:
        if os.path.basename(xep.path) == 'inbox':
            xslpath = os.path.abspath(os.path.join(xep.path, ".."))
        else:
            xslpath = xep.path

    for fle in ["xep.ent", "xep.dtd", "xep.xsl", "ref.xsl", "examples.xsl"]:
        shutil.copy(os.path.join(xslpath, fle), temppath)

    # XHTML
    outfile = open(
        os.path.join(outpath, "xep-{}.html".format(xep.nrFormatted)), "w")
    xsl = os.path.join(temppath, "xep.xsl")
    p = subprocess.Popen(["xsltproc", xsl, "-"],
                         stdin=subprocess.PIPE,
                         stdout=outfile,
                         stderr=subprocess.PIPE,
                         cwd=temppath)
    (dummy, error) = p.communicate(xep.raw)
    outfile.close()
    if error:
        xep.buildErrors.append(
            "Error while generating XHTML for {0}: {1}".format(str(xep), error))

    # Reference
    if not os.path.exists(os.path.join(outpath, "refs")):
        os.makedirs(os.path.join(outpath, "refs"))
    outfile = open(
        os.path.join(outpath, "refs", "reference.XSF.XEP-{}.xml".format(xep.nrFormatted)), "w")
    xsl = os.path.join(temppath, "ref.xsl")
    p = subprocess.Popen(["xsltproc", xsl, "-"],
                         stdin=subprocess.PIPE,
                         stdout=outfile,
                         stderr=subprocess.PIPE,
                         cwd=temppath)
    (dummy, error) = p.communicate(xep.raw)
    outfile.close()
    if error:
        xep.buildErrors.append(
            "Error while generating reference for {0}: {1}".format(str(xep), error))

    # Examples
    if not os.path.exists(os.path.join(outpath, "examples")):
        os.makedirs(os.path.join(outpath, "examples"))
    outfile = open(
        os.path.join(outpath, "examples", "{}.xml".format(xep.nrFormatted)), "w")
    xsl = os.path.join(temppath, "examples.xsl")
    p = subprocess.Popen(["xsltproc", xsl, "-"],
                         stdin=subprocess.PIPE,
                         stdout=outfile,
                         stderr=subprocess.PIPE,
                         cwd=temppath)
    (dummy, error) = p.communicate(xep.raw)
    outfile.close()
    if error:
        xep.buildErrors.append(
            "Error while generating examples for {0}: {1}".format(str(xep), error))

    # The source xml
    outfile = open(
        os.path.join(outpath, "xep-{}.xml".format(xep.nrFormatted)), "w")
    outfile.write(xep.raw)
    outfile.close()

    # Cleanup
    shutil.rmtree(temppath)


def buildPDF(xep, outpath=None, xslpath=None):
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
    outpath = xeputils.repository.prepDir(outpath)
    temppath = tempfile.mkdtemp(prefix='XEPbuilder_')
    if not xslpath:
        if os.path.basename(xep.path) == 'inbox':
            xslpath = os.path.abspath(os.path.join(xep.path, ".."))
        else:
            xslpath = xep.path

    for fle in ["xep.ent", "xep.dtd", "xep2texml.xsl", "../images/xmpp.pdf",
                "../images/xmpp-text.pdf", "deps/adjcalc.sty",
                "deps/collectbox.sty", "deps/tc-dvips.def", "deps/tc-pgf.def",
                "deps/trimclip.sty", "deps/adjustbox.sty", "deps/tabu.sty",
                "deps/tc-pdftex.def", "deps/tc-xetex.def"]:
        shutil.copy(os.path.join(xslpath, fle), temppath)

    # save inline images in tempdir
    for (no, img) in enumerate(xep.images):
        up = urlparse.urlparse(img)
        if up.scheme == 'data':
            head, data = up.path.split(',')
            # Tobias suggested to do something sensible with charset, mimetype
            # and encoding. I love the idea, but something tells me we will only
            # see these:
            if not head in ['image/png;base64', 'image/jpeg;base64']:
                raise Exception(
                    "Unknown encoding for inline image in {0}: {1}".format(str(xep), head))
            plaindata = base64.b64decode(data)
            mimetype = head.split(';')[0]
            fileext = mimetype.split('/')[1]
            imgfilename = os.path.join(
                temppath, 'inlineimage-{0}-{1:d}.{2}'.format(xep.nrFormatted, no, fileext))
            f = open(imgfilename, 'wb')
            f.write(plaindata)
            f.close()
        elif up.scheme in ['http', 'https']:
            request = urllib.urlopen(img)
            filename, fileext = os.path.splitext(up.path)
            if not fileext:
                fileext = ".{}".format(request.info().getsubtype())
            imgfilename = os.path.join(
                temppath, 'inlineimage-{0}-{1:d}{2}'.format(xep.nrFormatted, no, fileext))
            f = open(imgfilename, 'wb')
            f.write(request.read())
            f.close()
            request.close()

    texxmlfile = os.path.join(
        temppath, "xep-{}.tex.xml".format(xep.nrFormatted))
    texfile = os.path.join(temppath, "xep-{}.tex".format(xep.nrFormatted))

    # prepare for texml processing
    outfile = open(texxmlfile, "w")
    xsl = os.path.join(temppath, "xep2texml.xsl")
    p = subprocess.Popen(["xsltproc", xsl, "-"],
                         stdin=subprocess.PIPE,
                         stdout=outfile,
                         stderr=subprocess.PIPE,
                         cwd=temppath)
    (dummy, error) = p.communicate(xep.raw)
    outfile.close()
    if error:
        xep.buildErrors.append(
            "Error while generating tex.xml for {0}: {1}".format(str(xep), error))

    # Create TeX
    outfile = StringIO.StringIO()
    try:
        Texml.processor.process(
            in_stream=texxmlfile, out_stream=outfile, encoding="UTF-8")
    except Exception as msg:
        xep.buildErrors.append(
            "Error while converting xml to tex for {0}: {1}".format(str(xep), msg))
    finally:
        rawtex = outfile.getvalue()
        outfile.close()

    # detect http urls and escape them to make them breakable
    # this should match all urls in free text; not the urls in xml:ns or so..so no " or ' in front.
    # ToDo: check this regex, it may make some mismatches.
    rawtex = re.sub(r'([\s"])([^"]http://[^ \r\n"]*)', r'\1\\path{\2}', rawtex)
    # and escape the pond sign in the href
    rawtex = re.sub(r'\\href{([^#}]*)#([^}]*)}', r'\\href{\1\#\2}', rawtex)

    # adjust references, strip the leading pound sign.
    rawtex = re.sub(r'\\hyperref\[#([^\]]*)\]', r'\\hyperref[\1]', rawtex)
    rawtex = re.sub(r'\\pageref{#([^}]*)}', r'\\pageref{\1}', rawtex)

    f = open(texfile, "w")
    f.write(rawtex)
    f.close()

    # Build PDF
    # Do this multiple times, to build TOC and references
    for i in range(2):
        p = subprocess.Popen(["xelatex", "-interaction=batchmode", texfile],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd=temppath)
        (out, error) = p.communicate()
        if error:
            xep.buildErrors.append(
                "Error while generating PDF for {0}: {1} (pass {2})".format(str(xep), error, i))

    # move the PDF out of the way and clean up
    try:
        shutil.copy(
            os.path.join(temppath, "xep-{}.pdf".format(xep.nrFormatted)), outpath)
    except IOError:
        xep.buildErrors.append(
            "FATAL: Generating PDF for {} failed.".format(str(xep)))
    shutil.rmtree(temppath)
