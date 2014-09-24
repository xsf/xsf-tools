xsf-tools
=========

Automated tools for the management of XEPs at the XSF

Right now working towards automatically defering XEPs. For some thoughts on the
workflow see:
http://logs.xmpp.org/editor/2014-06-10/#18:36:56

For building XEPs it right now depends on:

* xsltproc (executable binary, debian package xsltproc)
* texml (python module, for source see: http://getfo.org)
* xelatex (executable binary, debian package texlive-xetex) Note: some recent
  versions have problems with correctly rendering images. Confirmed
  problematic: the versions from early 2014, confirmed working: the versions
  from july 2014.
* Aditionally xelatex needs some dependencies:
  * texlive-base (debian package)
  * texlive-xetex (debian package)
  * texlive-fonts-extra (debian package)
  * texlive-fonts-recommended (debian package)
  * texlive-latex-base (debian package)
  * texlive-latex-extra (debian package)
  * texlive-latex-recommended (debian package)
  * tipa (debian package)

For version control it right now depends on:

* git (executable binary, debian package git)

Executable scripts in this package:

* build.py - builds HTML and PDF from XEP XML sources
* cronjob.py - performs periodical maintanance tasks, right now deferring
* testscript.py - testscript for developers

All scripts have a help function that can be called with '-h'.

