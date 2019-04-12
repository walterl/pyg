"""
Contains functions that map AST nodes to string representations, on
which matching should be done.
"""

import ast
import sys


if sys.version_info.major > 2:
    basestring = str


def node_id(node):
    if hasattr(node, 'id') and isinstance(node.id, basestring):
        return node.id


def node_name(node):
    if hasattr(node, 'name') and isinstance(node.name, basestring):
        return node.name


def class_def(node):
    if isinstance(node, ast.ClassDef):
        return node.name


def function_def(node):
    if isinstance(node, ast.FunctionDef):
        return node.name


def call(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return node.func.id


def method_call(node):
    if not isinstance(node, ast.Call):
        return None

    func = node.func
    if not isinstance(func, ast.Attribute):
        return None

    strings = [func.attr]
    if isinstance(func.value, ast.Name):
        strings.extend([
            func.value.id, '{}.{}'.format(func.value.id, func.attr)
        ])

    return strings


def import_(node):
    if not isinstance(node, (ast.Import, ast.ImportFrom)):
        return None

    strings = []

    if isinstance(node, ast.ImportFrom) and node.module:
        strings.append(node.module)

    for alias in node.names:
        strings.append(alias.name)
        if alias.asname:
            strings.append(alias.asname)

    return strings
