import re
from typing import Any

import cuddle
import htpy
from markupsafe import escape, Markup


TAG: re.Pattern[Any] = re.compile(  # pyright: ignore[reportExplicitAny]
    r"(?P<tag>[a-zA-Z][a-zA-Z0-9_]*)?"  # pyright: ignore[reportImplicitStringConcatenation]
    r"(?P<cb>(?:\.[a-zA-Z_][a-zA-Z0-9_-]*)*)"
    r"(?P<id>#[a-zA-Z0-9_-]+)?"
    r"(?P<ca>(?:\.[a-zA-Z_][a-zA-Z0-9_-]*)*)"
)


def _htmlize(node: cuddle.Node) -> htpy.Fragment:
    if node.name == "_":
        if node.children or node.properties:
            raise ValueError(
                f"Text nodes cannot have children and/or properties: {node}",
            )
        return htpy.fragment[(escape(arg) for arg in node.arguments)]  # pyright: ignore[reportAny]
    try:
        tag_name: str | None
        classes_before: str
        tag_id: str | None
        classes_after: str
        tag_name, classes_before, tag_id, classes_after = TAG.fullmatch(node.name).groups()  # pyright: ignore[reportOptionalMemberAccess]
    except AttributeError:
        raise ValueError(f"Bad tag: {node.name}")
    try:
        tag = getattr(htpy, tag_name or "div")  # pyright: ignore[reportAny]
        if not isinstance(tag, (htpy.Element, htpy.VoidElement)):
            raise AttributeError()
    except AttributeError:
        raise ValueError(f"Unknown tag: {node.name}")
    else:
        el_args = ()
        el_kwargs = node.properties.copy()
        if classes_before or classes_after:
            el_args += (classes_before + classes_after,)
        if tag_id and "id" not in el_kwargs:  # latter "id" wins
            el_kwargs["id"] = tag_id.lstrip("#")
        el = tag(*el_args, **el_kwargs)  # pyright: ignore[reportCallIssue, reportArgumentType, reportUnknownVariableType]
        match el:
            case htpy.VoidElement() if node.arguments or node.children:
                raise TypeError(f"Void node {node.name} cannot have children")
            case htpy.VoidElement():
                return htpy.fragment[el(*node.arguments)]  # pyright: ignore[reportAny]
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
            case _:  # pyright: ignore[reportUnknownVariableType]
                raise RuntimeError("Impossible")


def htmlize(doc: cuddle.Document) -> htpy.Fragment:
    """Produce a htpy.Fragment from the cuddle.Document."""
    return htpy.fragment[map(_htmlize, doc.nodes)]
