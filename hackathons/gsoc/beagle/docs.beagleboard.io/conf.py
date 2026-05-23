# BeagleBoard.org documentation build configuration file.
# 
# References: 
# https://github.com/zephyrproject-rtos/zephyr/blob/main/doc/conf.py
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import re
import yaml
from pathlib import Path
import pydata_sphinx_theme
from sphinx.ext.imgconverter import ImagemagickConverter

# -- Banners --
announcement_message = ""
development_version_message = "This is a <strong>development version</strong> of docs."
forked_version_message = "This is a <strong>forked version</strong> of docs."
unknown_version_message = "This is an <strong>unknown version</strong> of docs."
version_link = "https://docs.beagleboard.org"
version_link_text = "Switch to released version"

# -- Project information --
project = 'BeagleBoard Docs'
copyright = '2024, BeagleBoard.org Foundation'
author = 'BeagleBoard.org Foundation'

ImagemagickConverter.conversion_rules.append(('image/webp', 'image/png'))

sys.path.append(str(Path(".").resolve()))

# Add latest images to rst_epilog
rst_epilog =""
rst_epilog_path = "_static/epilog/"
for (dirpath, dirnames, filenames) in os.walk(rst_epilog_path):
    for filename in filenames:
        with open(dirpath + filename) as f:
            rst_epilog += f.read()

# Configure PDF build and sidebar links
latex_documents = []
pdf_paths = []
oshw_details = []
board_details = []
book_details = []
project_details = []

with open('conf.yml', 'r') as conf_file:
    conf_data = yaml.safe_load(conf_file)

    pdf_build_all = True
    pdf_build = []
    if(conf_data["pdf_build"] != "all"):
        for name in conf_data["pdf_build"].split(","):
            pdf_build.append(name.lstrip())
        pdf_build_all = False

    for type, data in conf_data.items():
        # Boards
        if(type == "boards"):
            for board, data in conf_data["boards"].items():
                name = board
                path = data['path']
                pdf = data.get('pdf', False)
                page = data.get('page', False)
                git = data.get('git', False)
                forum = data.get('forum', False)
                
                # Board PDF build details
                if(pdf and (name in pdf_build or pdf_build_all)):
                    pdf_paths.append(path)
                    tex_name = '-'.join(path.split('/')[1:])
                    latex_documents.append((path+"/index", tex_name+".tex", "", author, "manual"))

                # Board OSHW mark details
                oshw_data = data.get('oshw', False)
                if oshw_data:
                    for oshw_mark_file in data['oshw'].split(','):
                        if oshw_mark_file.endswith('.svg'):
                            board, oshw_id = oshw_mark_file.lstrip().split(".")[0].split('_')
                            oshw_details.append([board, path, oshw_id])
                
                # Board basic details
                board_details.append([name, path, page, git, forum])
        
        # Books
        if(type == "books"):
            for book, data in conf_data["books"].items():
                name = book
                path = data['path']
                pdf = data.get('pdf', False)

                #Books PDF build details
                if(pdf and (name in pdf_build or pdf_build_all)):
                    pdf_paths.append(path)
                    tex_name = '-'.join(path.split('/')[1:])
                    latex_documents.append((path+"/index", tex_name+".tex", "", author, "manual"))

                # Book basic details
                book_details.append([name, path])

        # Projects
        if(type == "projects"):
            for book, data in conf_data["projects"].items():
                project = book
                path = data['path']
                pdf = data.get('pdf', False)

                #Projects PDF build details
                if(pdf and (project in pdf_build or pdf_build_all)):
                    pdf_paths.append(path)
                    tex_name = '-'.join(path.split('/')[1:])
                    latex_documents.append((path+"/index", tex_name+".tex", "", author, "manual"))

                # Project basic details
                project_details.append([name, path])

# -- General configuration --

sys.path.append(os.path.abspath("./_ext"))

extensions = [
    "callouts",
    "sphinxcontrib.rsvgconverter",
    "sphinx_design",
    "sphinxcontrib.images",
    "sphinx.ext.imgconverter",
    "sphinx.ext.graphviz",
    "sphinx.ext.todo",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinxext.rediraffe",
    "notfound.extension",
    "breathe",
    "exhale",
    "sphinx_copybutton",
    "sphinxcontrib.youtube",
]

# Initialize the rediraffe_redirects dictionary
rediraffe_redirects = {}
rediraffe_branch_excludes = [
    '_build',
    '_static',
    '_templates',
    '.*',     # Exclude hidden directories and files starting with '.'
    '*/_*',   # Exclude any directories starting with '_'
    '*/.*',   # Exclude any directories starting with '.'
]

# Automatically redirect all matching files
rediraffe_auto_redirect_perc = 100

# Define the mapping from old folders to new folders
redirect_folders = {
    "latest": "",  # Map from 'latest/' to the root directory
}

def is_excluded(path):
    """Check if any part of the path starts with '_' or '.'."""
    return any(part.startswith(('_', '.')) for part in path.parts)

# Loop through the files in the new folder and create redirects
for old_folder, new_folder in redirect_folders.items():
    # Ensure new_folder is '.' if it's empty (root directory)
    new_folder = new_folder or '.'

    # Convert new_folder to a Path object
    new_folder_path = Path(new_folder)

    # Iterate over all .rst and .md files in the new folder
    for newpath in new_folder_path.rglob("*"):
        # Exclude directories and files that start with '_' or '.'
        if is_excluded(newpath.relative_to(new_folder_path)):
            continue
        if newpath.is_file() and newpath.suffix in [".rst"]:
            # Build the old path by combining the old folder and the relative path of the new file
            oldpath = Path(old_folder) / newpath.relative_to(new_folder_path)
            # Add the mapping to rediraffe_redirects
            rediraffe_redirects[str(oldpath)] = str(newpath.relative_to(new_folder_path))

#graphviz_output_format = 'svg'

breathe_projects = {"librobotcontrol": "projects/librobotcontrol/docs/xml"}
breathe_default_project = "librobotcontrol"

exhale_args = {
    "containmentFolder": "./projects/librobotcontrol",
    "rootFileName": "index.rst",
    "rootFileTitle": "Robot Control Library",
    "createTreeView": True,
    "exhaleExecutesDoxygen": False,
    "doxygenStripFromPath": ".",
    "verboseBuild": False,
}

primary_domain = 'cpp'
highlight_language = 'cpp'

todo_include_todos = True

# Update (HTML) supported_image_types selection priority order
from sphinx.builders.html import StandaloneHTMLBuilder
StandaloneHTMLBuilder.supported_image_types = ['image/webp', 'image/jpg', 'image/jpeg', 'image/svg+xml', 'image/png', 'image/gif']

# Update (PDF) supported_image_types selection priority order
from sphinx.builders.latex import LaTeXBuilder
LaTeXBuilder.supported_image_types = ['application/pdf', 'image/jpg', 'image/jpeg', 'image/png']

templates_path = ['_templates']

source_suffix = ['.rst']
numfig = True

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'env', ".venv", '*/_*', '*/.*',]

# HTML 
html_theme = 'pydata_sphinx_theme'
html_static_path = ["_static"]
html_logo = "_static/images/logo.svg"
html_favicon = "_static/images/boris.svg"
html_sourcelink_suffix = ""
html_last_updated_fmt = ""
html_theme_path = [pydata_sphinx_theme.Path()]
html_title = "BeagleBoard Documentation"
html_baseurl = "docs.beagleboard.io"
html_css_files = [
    'css/custom.css',
]

# Pages entry without primary (left) sidebar

html_sidebars = {
    "**": ["sidebar-nav-bs", "mission"],
    "index": []
}

html_theme_options = {
    "external_links": [
        {
            "url": "https://www.beagleboard.org/about",
            "name": "About",
        },
        {
            "url": "https://www.beagleboard.org/donate",
            "name": "Donate",
        },
        {
            "url": "https://gsoc.beagleboard.org/",
            "name": "GSoC",
        },
        {
            "url": "https://forum.beagleboard.org/c/faq",
            "name": "FAQ",
        },
    ],
    # "header_links_before_dropdown": 4,
    "show_prev_next": True,
    "icon_links": [
        {
            "name": "OpenBeagle",
            "url": "https://openbeagle.org/",
            "icon": "fa-brands fa-gitlab",
            "attributes": {"target": "_blank"},
        },
        {
            "name": "Docs",
            "url": "https://docs.beagleboard.org/",
            "icon": "fa-solid fa-book",
            "attributes": {"target": "_blank"},
        },
        {
            "name": "Discord",
            "url": "https://bbb.io/discord",
            "icon": "fa-brands fa-discord",
            "attributes": {"target": "_blank"},
        },
        {
            "name": "Forum",
            "url": "https://forum.beagleboard.org/",
            "icon": "fa-brands fa-discourse",
            "attributes": {"target": "_blank"},
        },
        {
            "name": "BeagleBoard.org",
            "url": "https://www.beagleboard.org",
            "icon": "_static/images/boris.svg",
            "type": "local",
            "attributes": {"target": "_blank"},
        }
    ],
    "use_edit_page_button": True,
    "show_toc_level": 1,
    "navbar_align": "right",
    "show_nav_level": 1,
    "navbar_center": ["navbar-nav"],
    "navbar_start": ["navbar-logo"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    # "navbar_persistent": ["search-button"],
    "footer_start": ["copyright"],
    "footer_center": ["cc-by-sa"],
    "footer_end": ["last-updated"],
    # "content_footer_items": ["last-updated"],
    "secondary_sidebar_items": {
        "**": ["todo", "page-toc", "edit-this-page", "sourcelink","pdf", "feedback", "forum", "license-terms", "message", "oshw"]
    },
}

# Variables for gitlab pages
pages_url = ""
pages_slug = ""
gitlab_user = ""
gitlab_version = ""
gitlab_url = ""
gitlab_repo = ""
gitlab_project = ""

# parse pages details from 'PAGES' file
docs_url = ""
with open("PAGES") as f:
    m = re.match(
        (
            r"^PAGES_URL\s*=\s*(\S+)$\n"
            + r"^GITLAB_USER\s*=\s*(\S+)$\n"
            + r"^PROJECT_BRANCH\s*=\s*(\S+)$\n"
            + r"^GITLAB_HOST\s*=\s*(\S+)$\n"
            + r"^PROJECT_REPO\s*=\s*(\S+)$\n"
        ),
        f.read(),
        re.MULTILINE,
    )

    if not m:
        sys.stderr.write("Warning: Could not extract pages information\n")
    else:
        url, user, branch, host, repo = m.groups(1)
        pages_url = url
        gitlab_user = user
        gitlab_version = branch
        gitlab_url = host
        gitlab_repo = repo
        gitlab_project = "/".join((gitlab_url, gitlab_user, gitlab_repo))
        docs_url = url

# Specify the 404 template file
notfound_template = '404.html'

# Set the URLs prefix
if gitlab_user == 'docs':
    notfound_urls_prefix = '/'
elif gitlab_repo:
    notfound_urls_prefix =  '/' + gitlab_repo.strip('/') + '/'
else:
    notfound_urls_prefix = ''

# Provide additional context variables if needed
notfound_context = {
    'title': 'Page Not Found (404)',
}

html_context = {
    "display_gitlab": True,
    "gitlab_url": gitlab_url,
    "gitlab_user": gitlab_user,
    "gitlab_repo": gitlab_repo,
    "gitlab_version": gitlab_version,
    "gitlab_project": gitlab_project,
    "doc_path": "",
    #"use_edit_page_button": True,
    #"edit_page_url_template": "https://openbeagle.org/XXXX/{{ file_name }}",
    "conf_py_path": "",
    "show_license": True,
    "pages_url": pages_url,
    "pages_slug": pages_slug,
    "docs_url": docs_url,
    "edit_page_url_template": "{{ my_vcs_site }}{{ file_name }}",
    "edit_page_provider_name": "OpenBeagle",
    "my_vcs_site": "https://openbeagle.org/docs/docs.beagleboard.io/-/edit/main/",
    "oshw_details": oshw_details,
    "pdf_paths": pdf_paths,
    "board_details": board_details,
    "book_details": book_details,
    "project_details": project_details,
    "announcement_message": announcement_message,
    "development_version_message": development_version_message,
    "forked_version_message": forked_version_message,
    "unknown_version_message": unknown_version_message,
    "version_link": version_link,
    "version_link_text": version_link_text,
    "redirect_folders": redirect_folders,
}

# -- Options for LaTeX output --
latex_engine = "xelatex"
latex_logo = "_static/images/logo-latex.pdf"
latex_elements = {
    "papersize": "a4paper",
    "maketitle": open("_static/latex/title.tex").read(),
    "preamble": open("_static/latex/preamble.tex").read(),
    "sphinxsetup": ",".join(
        (
            "verbatimwithframe=false",
            "VerbatimColor={HTML}{f0f2f4}",
            "InnerLinkColor={HTML}{2980b9}",
            "warningBgColor={HTML}{e9a499}",
            "warningborder=0pt",
            r"HeaderFamily=\rmfamily\bfseries",
        )
    ),
}
