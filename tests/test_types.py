import pytest

import cdpy


def test_primitive_representation():
    # Int
    node_id = cdpy.dom.NodeId(123)
    assert str(node_id) == "NodeId(123)"
    assert repr(node_id) == "NodeId(123)"

    # Float
    timestamp = cdpy.runtime.Timestamp(9.123)
    assert str(timestamp) == "Timestamp(9.123)"
    assert repr(timestamp) == "Timestamp(9.123)"

    # String
    style_sheet_id = cdpy.css.StyleSheetId("c001")
    assert str(style_sheet_id) == "c001"
    assert repr(style_sheet_id) == "StyleSheetId('c001')"

    # Bool
    # None exist

    # List
    quad = cdpy.dom.Quad([3, 2, 1])
    assert str(quad) == "Quad([3, 2, 1])"
    assert repr(quad) == "Quad([3, 2, 1])"


def test_primitive_arithmetic():
    browser_id = cdpy.browser.WindowID(12)

    assert browser_id == 12
    assert browser_id + 5 == 17
    assert browser_id - 5 == 7
    assert browser_id * 2 == 24


def test_primitive_list():
    rectangle = cdpy.dom_snapshot.Rectangle([1, 2, 3])
    assert rectangle == [1, 2, 3]

    rectangle.append(4)
    assert rectangle == [1, 2, 3, 4]

    rectangle += [5, 6]
    assert rectangle == [1, 2, 3, 4, 5, 6]

    # Element access
    assert rectangle[3] == 4
    assert rectangle[-1] == 6
    assert rectangle[1:] == [2, 3, 4, 5, 6]
    assert rectangle[:2] == [1, 2]
