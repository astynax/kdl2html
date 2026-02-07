from typing import Never

import cuddle
import htpy
from markupsafe import escape, Markup


def _htmlize(node: cuddle.Node) -> htpy.Fragment:
    if node.name == "_":
        if node.children or node.properties:
            raise ValueError(
                f"Text nodes cannot have children and/or properties: {node}",
            )
        return htpy.fragment[(escape(arg) for arg in node.arguments)]  # pyright: ignore[reportAny]
    try:
        tag = getattr(htpy, node.name)  # pyright: ignore[reportAny]
        if not isinstance(tag, (htpy.Element, htpy.VoidElement)):
            raise AttributeError()
    except AttributeError:
        raise ValueError(f"Unknown tag: {node.name}")
    else:
        el = tag(**node.properties)  # pyright: ignore[reportAny]
        match el:
            case htpy.VoidElement() if node.arguments or node.children:
                raise TypeError(f"Void node {node.name} cannot have children")
            case htpy.Element():
                if tag is htpy.script or tag is htpy.style:
                    if len(node.arguments) > 1 or node.children:
                        raise ValueError(
                            "Script and style tags should have"  # pyright: ignore[reportImplicitStringConcatenation]
                            " exatcly one (raw) string argument"
                        )
                    args = (
                        (Markup(arg) for arg in node.arguments),  # pyright: ignore[reportAny]
                    )
                else:
                    args = (
                        (htpy.fragment[escape(arg)] for arg in node.arguments),  # pyright: ignore[reportAny]
                        map(_htmlize, node.children),
                    )
                return htpy.fragment[el[*args]]
            case _:
                raise RuntimeError("Impossible")


def htmlize(doc: cuddle.Document) -> htpy.Fragment:
    """Produce a htpy.Fragment string from the cuddle.Document."""
    return htpy.fragment[map(_htmlize, doc.nodes)]
