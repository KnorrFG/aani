import contextlib
import os
from pathlib import Path

from aani import aani

doc_doc_script = aani.DocumentedPathTreeNode("doc_script.py", 
        "Im a docmented Script.\n\nI also have a detailed description", frozenset())
doc_undoc_script = aani.DocumentedPathTreeNode("undoc_script.py", "", frozenset())
undoc_doc_script = aani.DocumentedPathTreeNode("doc_script.py", 
        "Im a docmented Script.\n\nI also have a detailed description", frozenset())
undoc_undoc_script = aani.DocumentedPathTreeNode("undoc_script.py", "", frozenset())
doc_dir = aani.DocumentedPathTreeNode("documented", 
    "Short description. Bla bla\n\nLonger, more detailed description", 
    frozenset([doc_doc_script, doc_undoc_script]))
undoc_dir = aani.DocumentedPathTreeNode("undocumented", "",
        frozenset([undoc_doc_script, undoc_undoc_script]))
doc_html = aani.DocumentedPathTreeNode("documentation.html", "",
        frozenset())
test_tree = aani.DocumentedPathTreeNode("test_dir", "Main-Readme.", 
        frozenset([doc_dir, undoc_dir, doc_html]))


def test_build_tree():
    # with temp_chdir("test_dir"):
    ign_patterns = Path('test_dir/.gitignore').read_text().splitlines()\
            + aani.ignore_additions
    tree = aani.build_tree(Path("test_dir"), ign_patterns)
    assert tree == test_tree

