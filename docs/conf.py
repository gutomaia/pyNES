import sys
import os
import time
sys.path.insert(0, os.path.abspath(".."))
import shlex
import sphinx_rtd_theme

# Project Properties

project = u'pyNES'
description = u'write NES games in Python'
copyright = u'2012-%s, Guto Maia' % time.strftime('%Y')
author = u'Guto Maia'
version = '0.2'
release = '0.2.1'

# Document Properties

master_doc = 'index'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
]

# templates_path = ['_templates']
source_suffix = '.rst'

primary_domain = 'py'
default_role = 'py:obj'
autodoc_member_order = "bysource"
autoclass_content = "both"

autodoc_docstring_signature = True



language = None

exclude_patterns = ['_build']

pygments_style = 'sphinx'

todo_include_todos = True


html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
# html_static_path = ['_static']
htmlhelp_basename = 'pyNESdoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

# Latex figure (float) alignment
#'figure_align': 'htbp',
}

latex_documents = [
  (master_doc, 'pyNES.tex', u'pyNES Documentation',
   u'Guto Maia', 'manual'),
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    (master_doc, 'pynes', u'pyNES Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
  (master_doc, 'pyNES', u'pyNES Documentation',
   author, 'pyNES', description,
   'Miscellaneous'),
]

intersphinx_mapping = {'https://docs.python.org/': None}
