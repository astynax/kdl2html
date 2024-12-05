#!/usr/bin/env -S uv run --no-project --quiet
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "cuddle==1.0.6",
#     "htpy==24.10.1",
# ]
# ///

import sys
from itertools import chain

import htpy
from markupsafe import Markup
import cuddle


def htmlize(node: cuddle.Node | cuddle.Document) -> str:
    if isinstance(node, cuddle.Document):
        return ''.join(str(htmlize(n)) for n in node.nodes)
    el = getattr(htpy, node.name)(**node.properties)
    if not isinstance(el, htpy.VoidElement):
        el = el[list(chain(
            (Markup(str(a)) for a in node.arguments),
            map(htmlize, node.children),
        ))]
    elif node.arguments or node.children:
        raise TypeError("Void node", node.name, "cannot have children")
    return el


def main():
    print(htmlize(cuddle.load(sys.stdin)))


if __name__ == '__main__':
    main()
