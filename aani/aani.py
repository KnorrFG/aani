from __future__ import annotations

import importlib.resources as imres
import subprocess as sp
import textwrap as tw
from fnmatch import fnmatch
from itertools import count, chain
from pathlib import Path
from typing import FrozenSet, Iterable, List, NamedTuple, Optional

import click
import markdown
from pyhtml import *

from . import resources

ignore_additions = ['.*', '__*', '**/__*', 'readme.md', '**/readme.md']

class DocumentedPathTreeNode(NamedTuple):
    name: str
    doc: Optional[str]
    children: FrozenSet[DocumentedPathTreeNode]
    path: Path
    id: int

    def print(self, indent=0):
        '''Only used for Debugging'''
        sindent = ('  ' * indent)
        print(sindent + self.name)
        if self.doc:
            docindent = 2 * (indent + 1)
            print(tw.indent(tw.fill('"""' + self.doc + '"""', 70 - docindent),
                ' ' * docindent))
            print()
        for child in self.children:
            child.print(indent + 1)


def md2html(md: str):
    return markdown.markdown(md, extensions=['extra', 'toc'])


def read_if_exists(path: Path):
    if path.exists():
        return path.read_text().strip()
    return ""


def make_dir_node(dir: Path, children: set, counter)\
        -> DocumentedPathTreeNode:
    return DocumentedPathTreeNode(dir.name, 
            read_if_exists(dir / 'readme.md'), frozenset(children),
            dir, next(counter))


def get_py_doc_str(s: str):
    stripped = s.strip()
    if stripped.startswith('"""'):
        end = stripped[1:].find('"""') + 1
    elif stripped.startswith("'''"):
        end = stripped[1:].find("'''") + 1
    else:
        end = -1
    
    if end == -1:
        return ""
    else:
        return stripped[3:end]


def make_file_node(file: Path, counter):
    if file.suffix == '.py':
        doc = get_py_doc_str(file.read_text())
    else:
        doc = ''
    return DocumentedPathTreeNode(file.name, doc, frozenset(), file, next(counter))


def build_tree(dir: Path, counter: Iterable[int],  
               ign_patterns: List[str], root=None) -> DocumentedPathTreeNode:
    children = set()
    if root is None:
        dir = dir.absolute()
        root = dir
    for p in dir.iterdir():
        if any(fnmatch(str(p.relative_to(root)), ip) for ip in ign_patterns):
            continue
        if p.is_dir():
            children.add(build_tree(p, counter, ign_patterns, root))
        else:
            children.add(make_file_node(p, counter))
    return make_dir_node(dir, children, counter)
            

def spacify(s: str) -> str:
    return s.replace('-', ' ').replace('_', ' ')


def short_doc(s: str) -> str:
    end = s.find('\n\n')
    if end != -1:
        return s[:end]
    else:
        return s


def tree_node_sorter(node: DocumentedPathTreeNode):
    return (1 if len(node.children) else 0, node.name)


def make_short_overview(tree: DocumentedPathTreeNode, is_root: bool = True):
    if tree.path.is_file():
        thisli = lambda *x: li(_safe=True)("&#x1f5ce;", *x)
    else:
        thisli = lambda *x: li(_safe=True, class_="folder")("&#128193;", *x)

    if tree.doc and not is_root:
        self_desc = thisli(
            div(a(href=f'#tid{tree.id}')(tree.name)),
            div(" - "),
            div(class_='shortdoc')(span(i(short_doc(tree.doc)))))
    else:
        self_desc = thisli(tree.name)

    if len(tree.children) > 0:
        return (self_desc,
                ul(*[make_short_overview(child, is_root=False) 
                    for child in sorted(tree.children, 
                        key=tree_node_sorter)]))
    else:
        return self_desc


def iter_documented_folders(tree: DocumentedPathTreeNode, 
                            is_root: bool = True) ->\
        Iterable[DocumentedPathTreeNode]:
    if tree.path.is_dir() and tree.doc and not is_root:
        yield tree
        
    for child in tree.children:
        yield from iter_documented_folders(child, is_root=False)


def iter_documented_files(tree: DocumentedPathTreeNode) ->\
        Iterable[DocumentedPathTreeNode]:
    if tree.path.is_file() and tree.doc:
        yield tree
        
    for child in tree.children:
        yield from iter_documented_files(child)


def make_doc_dl_list_from_iter(tree: DocumentedPathTreeNode, iter):
    defs = chain.from_iterable(
            (dt(id=f'tid{node.id}')(str(node.path.relative_to(tree.path))), 
             dd(node.doc)) 
            for node in sorted(iter, key=lambda x: x.path))
    return dl(*defs)


def make_folder_doc(tree):
    return make_doc_dl_list_from_iter(tree, iter_documented_folders(tree))


def make_file_doc(tree: DocumentedPathTreeNode):
    return make_doc_dl_list_from_iter(tree, iter_documented_files(tree))


def make_html(tree: DocumentedPathTreeNode) -> str:
    body_elems = []
    doctitle = f'{spacify(tree.name).capitalize()} Documentation'
    body_elems.append(h1(doctitle))
    if tree.doc:
        body_elems.append(a(href='#index')("Go to file index"))
        body_elems.append(md2html(tree.doc))
    body_elems.append(h2(id='index')("Index"))
    body_elems.append(div(class_="short_overview")(
        ul(class_="dirtree")(make_short_overview(tree))))
    body_elems.append(h2("Folder Doc"))
    body_elems.append(make_folder_doc(tree))
    body_elems.append(h2("File Doc"))
    body_elems.append(make_file_doc(tree))
    return str(html(
            head(meta(charset="UTF-8"),
                 title(doctitle),
                 style(_safe=True)(imres.read_text(resources, "pandoc.css"))),
            body(_safe=True)(*body_elems)))


@click.command()
@click.argument('dir', type=Path, default=Path())
@click.argument('output', type=Path, default=None, required=False) 
@click.option('--print-html', '-p', is_flag=True)
def cli(dir: Path, output: Optional[Path], print_html: bool):
    """Generates a project documentation in the given directory"""
    gitignore_path = dir / '.gitignore'
    gitignore_patterns = (gitignore_path.read_text().splitlines() if
            gitignore_path.exists() else []) + ignore_additions
    tree = build_tree(dir, count(0), gitignore_patterns)
    html = make_html(tree)
    if print_html:
        print(html)
        return 0

    output = output or (dir / 'documentation.html')
    output.write_text(html)
