# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute.

import os
import sys

os.environ["GENERATING_SPHINX_DOCS"] = ""
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), os.pardir)))  # go up a folder to access scripts


# -- Project information -----------------------------------------------------

project = 'NotQuiteParadise2'
copyright = '2019-2022, Josh Snaith'
author = 'Josh Snaith (Snayff)'

# The short X.Y version
version = "0.0.1"


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    #'sphinx_autodoc_typehints',  # causes circular error with snecs
    'sphinx_autodoc_annotation',
    #'sphinx_git',  # causes CI to fail with git error code 128
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = ['.rst']  # , '.txt'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%d %b %y at %H:%M'

# A boolean that decides whether module names are prepended to all object names (for object types where a “module” of
# some kind is defined), e.g. for py:function directives. Default is True.
add_module_names = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'karma_sphinx_theme'
# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

# https://bashtage.github.io/sphinx-material/
# Material theme options (see theme.conf for more information)
html_theme_options = {}

# material theme options:
#     {
#
#     # Set the name of the project to appear in the navigation.
#     'nav_title': 'Not Quite Paradise 2',
#
#     # Specify a base_url used to generate sitemap.xml. If not
#     # specified, then no sitemap will be built.
#     'base_url': 'https://snayff.github.io/nqp2/',
#
#     # Set the color and the accent color
#     'color_primary': 'deep-purple',
#     'color_accent': 'deep-orange',
#
#     # Set the repo location to get a badge with stats
#     'repo_url': 'https://github.com/Snayff/nqp2',
#     'repo_name': 'Not Quite Paradise',
#
#     # Visible levels of the global TOC; -1 means unlimited
#     'globaltoc_depth': 3,
#     # If False, expand all TOC entries
#     'globaltoc_collapse': True,
#
#     'html_minify': False,
#     'css_minify': True,
#     # Set the logo icon. Should be a pre-escaped html string that indicates a unicode point
#     'logo_icon': '&#xe869',
#     'master_doc': True,
#
#}

html_show_sourcelink = True
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'NotQuiteParadisedoc'


# -- Options for LaTeX output ------------------------------------------------

# latex_elements = {
#     # The paper size ('letterpaper' or 'a4paper').
#     #
#     # 'papersize': 'letterpaper',
#
#     # The font size ('10pt', '11pt' or '12pt').
#     #
#     # 'pointsize': '10pt',
#
#     # Additional stuff for the LaTeX preamble.
#     #
#     # 'preamble': '',
#
#     # Latex figure (float) alignment
#     #
#     # 'figure_align': 'htbp',
# }
#
# # Grouping the document tree into LaTeX files. List of tuples
# # (source start file, target name, title,
# #  author, documentclass [howto, manual, or own class]).
# latex_documents = [
#     (master_doc, 'NotQuiteParadise.tex', 'NotQuiteParadise Documentation',
#      'Snayff', 'manual'),
# ]
#
#
# # -- Options for manual page output ------------------------------------------
#
# # One entry per manual page. List of tuples
# # (source start file, name, description, authors, manual section).
# # man_pages = [
# #     (master_doc, 'notquiteparadise', 'NotQuiteParadise Documentation',
# #      [author], 1)
# # ]
#
#
# # -- Options for Texinfo output ----------------------------------------------
#
# # Grouping the document tree into Texinfo files. List of tuples
# # (source start file, target name, title, author,
# #  dir menu entry, description, category)
# texinfo_documents = [
#     (master_doc, 'NotQuiteParadise', 'NotQuiteParadise Documentation',
#      author, 'NotQuiteParadise', 'A game about dreams.',
#      '???'),
# ]
#
#
# # -- Options for Epub output -------------------------------------------------
#
# # Bibliographic Dublin Core info.
# epub_title = project
#
# # The unique identifier of the text. This can be a ISBN number
# # or the project homepage.
# #
# # epub_identifier = ''
#
# # A unique identification for the text.
# #
# # epub_uid = ''
#
# # A list of files that should not be packed into the epub file.
# epub_exclude_files = ['search.html']


# -- Extension configuration -------------------------------------------------

# -- sphinx.ext.intersphinx  ---------------------------------------

intersphinx_mapping = {
    'https://docs.python.org/3/': None,
    'https://pygame-gui.readthedocs.io/en/latest/': None,
    'https://www.pygame.org/docs/': None,
    'https://snayff.github.io/nqp2/': None,
}

# -- sphinx.ext.todo ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
# looks for ".. todo::` for individual todo comments
todo_include_todos = True


# -- sphinx.ext.autdoc ----------------------------------------------------------------
# Auiodoc settings
autodoc_default_options = {
    'members': True,
    'ignore-module-all': True,
    'special-members': '__init__',
    'show-inheritance': True,
#     'member-order': 'bysource',
     'undoc-members': True,
#     'private-members': True,  # Dont set to False. There is a bug that causes the build to break.
}
autoclass_content = "both"

# -- sphinx-autodoc-typehints ---------------------------------------------------
always_document_param_types = True
set_type_checking_flag = True
typehints_document_rtype = True

# -- sphinx.ext.autosectionlabel ---------------------------------------------------
# True to prefix each section label with the name of the document it is in, followed by a colon. For example, index:Introduction for a section called Introduction that appears in document index.rst. Useful for avoiding ambiguity when the same section heading appears in different documents.
# autosectionlabel_prefix_document

# If set, autosectionlabel chooses the sections for labeling by its depth. For example, when set 1 to autosectionlabel_maxdepth, labels are generated only for top level sections, and deeper sections are not labeled. It defaults to None (disabled).
autosectionlabel_maxdepth = 2

# -- sphinx.ext.viewcode ---------------------------------------------------
viewcode_follow_imported_members = True
