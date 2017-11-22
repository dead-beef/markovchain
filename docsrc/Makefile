# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = markovchain
SOURCEDIR     = .
BUILDDIR      = _build
HTML_DIR      := $(BUILDDIR)/html
DISTDIR       = ../docs

$(DISTDIR) $(BUILDDIR):
	mkdir -p $@

$(HTML_DIR): | $(DISTDIR) $(BUILDDIR)
	ln -s ../$(DISTDIR) $@

apidoc:
	sphinx-apidoc -o source/ ../$(SPHINXPROJ)

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile | $(HTML_DIR)
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
