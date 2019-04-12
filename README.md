# pyg (PYthon Grep): Python syntax-aware grep

Pronounced *pig*.

    $ ./pyg.py --help
    usage: pyg.py [-h] [--verbose] [--ignore-case] [--files-with-matches]
                [--elem ELEM]
                PATTERN [PATH]

    PYthon Grep

    positional arguments:
    PATTERN               Pattern to search for.
    PATH

    optional arguments:
    -h, --help            show this help message and exit
    --verbose, -v
    --ignore-case, -i     Match case insensitively.
    --files-with-matches, -l
                          Only print names of files containing matches, not
                          matching lines.
    --elem ELEM, -e ELEM  Language elements to match on. Value must contain any
                          of the following characters: [c]all, [d]ef, [i]mports,
                          [k]lass, [m]ethod calls

Grep for lines in Python files that contain `hlight`:

    $ ./pyg.py high
    pyg.py:34:        from pygments import highlight
    pyg.py:46:    return highlight(src, hilite._lexer, hilite._formatter).rstrip()

Grep for lines containing function calls containing `hlight`:

    $ ./pyg.py -e c hlight
    pyg.py:46:    return highlight(src, hilite._lexer, hilite._formatter).rstrip()



## Features

* grep-compatible output
* Automatic syntax highlighting if [`pygments`](http://pygments.org/) is found.


## Implementation

Parses each Python source file (`.py` and `.pyx`) with the
[`ast`](https://docs.python.org/3.6/library/ast.html) module. The AST tree is
then searched for nodes matching the specified type, and pattern. The
line-and-file information for each match is printed.

Works in Python 2 and 3.


## Usage in vim

    :set grepprg=/path/to/pyg.py
    :grep -e i hlight


## Shameless plug

Released, with permission, as a utility developed in the course of my work at
[CheckSec](https://checksec.com/). If you are part of a penetration testing
team, you probably want to have a look at CheckSec's
[Canopy](https://checksec.com/canopy.html).


## License

[LGPLv3](https://github.com/walterl/pyg/blob/master/LICENSE)
