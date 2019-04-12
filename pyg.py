#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import ast
import logging
import os
import re
import sys

import nodestrings


DOTSLASH = os.curdir + os.sep
SOURCE_FILE_EXTENSIONS = ('.py', '.pyx')

logging.basicConfig()
log = logging.getLogger()


def listify(x):
    if isinstance(x, (list, tuple)):
        return x
    return [x] if x is not None else []


def hilite(src):
    if not sys.stdout.isatty():
        return src

    try:
        from pygments import highlight
        from pygments.formatters import TerminalFormatter
        from pygments.lexers import PythonLexer
    except ImportError:
        # Can't find pygments, so we can't highlight
        return src

    if not hasattr(hilite, '_lexer'):
        setattr(hilite, '_lexer', PythonLexer())
    if not hasattr(hilite, '_formatter'):
        setattr(hilite, '_formatter', TerminalFormatter())

    return highlight(src, hilite._lexer, hilite._formatter).rstrip()


def expand_path(path):
    if path is None:
        path = os.curdir

    if os.path.isfile(path):
        yield path
        return

    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                ext = os.path.splitext(filename)[-1]
                if ext not in SOURCE_FILE_EXTENSIONS:
                    continue

                fullpath = os.path.join(dirpath, filename)
                if fullpath.startswith(DOTSLASH):
                    fullpath = fullpath[len(DOTSLASH):]

                log.debug('Source file: {}'.format(fullpath))
                yield fullpath


def collect_string_fns(options):
    if options is None:
        options = {}

    fns = []
    for attr in dir(nodestrings):
        attr_value = getattr(nodestrings, attr)
        if callable(attr_value):
            fns.append(attr_value)

    if not options:
        # Use all stringifiers if no specific ones are requested.
        return fns

    fns = []

    if options.get('include_calls'):
        fns.append(nodestrings.call)

    if options.get('include_function_defs'):
        fns.append(nodestrings.function_def)

    if options.get('include_imports'):
        fns.append(nodestrings.import_)

    if options.get('include_class_defs'):
        fns.append(nodestrings.class_def)

    if options.get('include_method_calls'):
        fns.append(nodestrings.method_call)

    return fns


def grep(pattern, filepaths, options=None):
    seen_lines = set()
    rx = re.compile(pattern)

    string_fns = collect_string_fns(options)
    log.debug('String functions: %r', string_fns)

    for filepath in filepaths:
        log.debug('file: %r', filepath)
        lines = open(filepath).read().split('\n')
        try:
            ast_root = ast.parse('\n'.join(lines), filename=filepath)
        except Exception:
            log.debug('Unable to parse %r:', filepath)
            continue

        for node in ast.walk(ast_root):
            if not hasattr(node, 'lineno'):
                continue

            ids = set()
            for fn in string_fns:
                for strings in listify(fn(node)):
                    ids.add(strings)

            seen_key = (filepath, node.lineno)
            for nid in ids:
                if rx.search(nid) and seen_key not in seen_lines:
                    seen_lines.add(seen_key)
                    match = '{}:{}:{}'.format(
                        filepath, node.lineno, hilite(lines[node.lineno-1])
                    )
                    yield match
                    break


def create_arg_parser():
    parser = argparse.ArgumentParser(description='PYthon Grep')

    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('PATTERN', help='Pattern to search for.')
    parser.add_argument('PATH', nargs='?')

    # Python language syntax filters
    parser.add_argument(
        '--elem', '-e', default='',
        help=(
            'Language elements to match on. Value must contain any of the '
            'following characters: [c]all, [d]ef, [i]mports, [k]lass, '
            '[m]ethod calls'
        )
    )

    return parser


def main():
    args = create_arg_parser().parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        log.debug('Debug logging enabled')

    elem_options = {
        'c': 'include_calls',
        'd': 'include_function_defs',
        'i': 'include_imports',
        'k': 'include_class_defs',
        'm': 'include_method_calls',
    }

    options = {}
    for char in args.elem:
        if char not in elem_options:
            raise ValueError('Invalid language element option: %r' % (char,))
        options[elem_options[char]] = True

    had_results = False
    for result in grep(args.PATTERN, expand_path(args.PATH), options=options):
        had_results = True
        print result

    if not had_results:
        exit(1)


if __name__ == "__main__":
    main()
