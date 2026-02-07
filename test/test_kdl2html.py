import htpy as h
import cuddle as c

from kdl2html import htmlize


def doc(source: str) -> str:
    return str(htmlize(c.loads(source)))  # pyright: ignore[reportUnknownMemberType]


def test_htmlize_doc_to_doc():
    assert str(h.fragment[
        h.h1["Example"],
        h.div(".red")[
            "This", h.span["<span>"], "is red"
        ]
    ]) == str(htmlize(c.Document(nodes=c.NodeList([
        c.Node("h1", None, arguments=["Example"]),
        c.Node("div", None, properties={"class": "red"}, children=[
            c.Node("_", None, arguments=["This"]),
            c.Node("span", None, arguments=["<span>"]),
            c.Node("_", None, arguments=["is", " ", "red"]),
        ]),
    ]))))


def test_htmlize_actual_kdl():
    assert str(h.fragment[
        h.h1["Example"],
        h.div(".red")[
            "This", h.span["<span>"], "is red"
        ]
    ]) == doc("""
h1 "Example"
div class="red" {
    _ "This"
    span "<span>"
    _ "is" " " "red"
}
""")


def test_text_node_argument_joining():
    assert doc('_ "foo" "" "bar"') == doc('_ "foobar"')
