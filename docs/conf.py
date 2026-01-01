# -*- coding: utf-8 -*-
import os
import sys

# Dodanie ścieżki src, aby Sphinx mógł generować dokumentację z docstringów
sys.path.insert(0, os.path.abspath('../src'))

# -- General configuration -----------------------------------------------------

# Rozszerzenia Sphinx
extensions = [
    'sphinx.ext.autodoc',      # Generowanie dokumentacji z docstringów
    'sphinx.ext.viewcode',     # Dodawanie linków do kodu źródłowego
    'sphinx.ext.napoleon',     # Obsługa docstringów w stylu Google/NumPy
    'sphinxcontrib.mermaid'    # Obsługa diagramów Mermaid
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# Informacje o projekcie
project = u'Scientometrics Simulation System (S3)'
copyright = u'2025, kabix09'
author = u'kabix09'

# Wersja projektu
version = u'1.0'
release = u'1.0.0'

# Język dokumentacji
language = 'pl'

# Lista wzorców do ignorowania
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Styl podświetlania składni
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------

# Użycie motywu Read the Docs (wymaga: pip install sphinx_rtd_theme)
html_theme = 'sphinx_rtd_theme'

# Dodatkowe ustawienia motywu (opcjonalnie)
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
}

html_static_path = ['_static']

# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
}

latex_documents = [
    ('index', 'Scientometrics_S3.tex', u'Scientometrics Simulation System (S3) Documentation',
     u'kabix09', 'manual'),
]