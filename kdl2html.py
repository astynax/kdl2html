import sys

import htpy
from markupsafe import escape, Markup
import cuddle


def _htmlize(node: cuddle.Node) -> htpy.Fragment:
    if node.name == "_":
        if node.children or node.properties:
            raise ValueError(
                f"Text nodes cannot have children and/or properties: {node}",
            )
        return htpy.fragment[(escape(arg) for arg in node.arguments)]
    try:
        tag: htpy.Element | htpy.VoidElement
        tag = getattr(htpy, node.name)
    except AttributeError:
        raise ValueError(f"Unknown tag: {node.name}")
    else:
        el = tag(**node.properties)
        match el:
            case htpy.VoidElement() if node.arguments or node.children:
                raise TypeError(f"Void node {node.name} cannot have children")
            case htpy.Element():
                if tag is htpy.script or tag is htpy.style:
                    if len(node.arguments) > 1 or node.children:
                        raise ValueError("Script and style tags should have"
                                         " exatcly one (raw) string argument")
                    args = (
                        (Markup(arg) for arg in node.arguments),
                    )
                else:
                    args = (
                        (htpy.fragment[escape(arg)] for arg in node.arguments),
                        map(_htmlize, node.children),
                    )
                return htpy.fragment[el[*args]]
            case _:
                return htpy.fragment[el]


def htmlize(doc: cuddle.Document) -> str:
    return str(htpy.fragment[map(_htmlize, doc.nodes)])


def main():
    print(htmlize(cuddle.load(sys.stdin)))


if __name__ == '__main__':
    main()
