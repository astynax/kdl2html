import htpy as h
import cuddle as c

from kdl2html import htmlize, TAG
import pytest


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


def test_tag_pattern():
    def m(text: str) -> tuple[str | None, str, str | None, str]:
        return TAG.fullmatch(text).groups()  # pyright: ignore[reportOptionalMemberAccess, reportReturnType]

    assert m("div") == ("div", "", None, "")
    assert m("#foo") == (None, "", "#foo", "")
    assert m("span.dark-red#_anchor.light.bold") == (
        "span", ".dark-red", "#_anchor", ".light.bold",
    )


def test_id_and_classes_syntax():
    assert doc(".nav") == doc('div class="nav"')
    assert doc("#foo") == doc('div id="foo"')
    assert doc('span.dark-red#_anchor.light.bold') == doc(
        'span class="dark-red light bold" id="_anchor"'
    )
    assert doc('span.dark-red#_anchor.light.bold id="foo"') == doc(
        'span class="dark-red light bold" id="foo"'
    )
    with pytest.raises(ValueError):
        assert doc("div##bar")
    with pytest.raises(ValueError):
        assert doc("div,a,b")
    with pytest.raises(ValueError):
        assert doc("1div")
    with pytest.raises(ValueError):
        assert doc("#foo#bar")
