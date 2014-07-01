xsf-tools
=========

Automated tools for the management of XEPs at the XSF

Right now working towards automatically defering XEPs. For some thoughts on the workflow see:
http://logs.xmpp.org/editor/2014-06-10/#18:36:56

For building XEPs it right now depends on:

* xsltproc (executable binary, debian package xsltproc)
* texml (python module, for source see: http://getfo.org)
* xelatex (executable binary, debian package texlive-xetex)
* Aditionally xelatex needs some dependencies:
  * texlive-base (debian package)
  * texlive-xetex (debian package)
  * texlive-fonts-extra (debian package)
  * texlive-fonts-recommended (debian package)
  * texlive-latex-base (debian package)
  * texlive-latex-extra (debian package)
  * texlive-latex-recommended (debian package)
  * tipa (debian package)

Usage (for testscript):

```
$ cd extensions
$ python ../../path_to_scripts/testscript.py
```

This testscript reads all XEPs (xml files) in the current directory, performs
some tests on them and then tries to build them all to HTML and PDF format.

