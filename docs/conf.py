# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pkg_resources import get_distribution, DistributionNotFound
from sphinx.domains.python import PythonDomain

sys.path.insert(0, os.path.abspath(os.path.expanduser("../src")))



# -- Project information -----------------------------------------------------

project = 'gridengineapp'
copyright = '2019, Drew Dolgert'
author = 'Drew Dolgert'
try:
    release = get_distribution('cascade').version
except DistributionNotFound:
    release = "19.3.0"

# The short X.Y version.
version = '.'.join(release.split('.')[:2])


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinxcontrib.napoleon",  # for easy line breaks
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# -- Autodoc configuration ------------------------------------------------

# Sort order of members listed by autodoc
# options are: 'alphabetical', 'groupwise', or 'bysource'
autodoc_member_order = "bysource"

# Defaults for automodule and autoclass
# To negate add `:no-undoc-members:` flag to a particular instance
autodoc_default_flags = []

# Can't mock numpy because it causes a LooseVersion error.
autodoc_mock_imports = [
    "networkx",
]

# This patch is here to turn off warnings about duplicate documentation.
# We put things in references.
class PatchedPythonDomain(PythonDomain):
    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        if 'refspecific' in node:
            del node['refspecific']
        return super(PatchedPythonDomain, self).resolve_xref(
            env, fromdocname, builder, typ, target, node, contnode)


def setup(sphinx):
    sphinx.add_domain(PatchedPythonDomain, override=True)
