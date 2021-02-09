from enum import Enum

import pytest
from pytest import approx

import cdpy


@pytest.fixture
def node_id():
    return cdpy.dom.NodeId(123)


@pytest.fixture
def timestamp():
    return cdpy.runtime.Timestamp(9.123)


@pytest.fixture
def style_sheet_id():
    return cdpy.css.StyleSheetId("c001")


@pytest.fixture
def pseudo_type():
    return cdpy.dom.PseudoType("before")


@pytest.fixture
def quad():
    return cdpy.dom.Quad([3, 2, 1])


class TestSubclass:
    def test_int(self, node_id):
        assert issubclass(type(node_id), int)

    def test_float(self, timestamp):
        assert issubclass(type(timestamp), float)

    def test_string(self, style_sheet_id):
        assert issubclass(type(style_sheet_id), str)

    def test_list_of_builtins(self, quad):
        assert issubclass(type(quad), list)

    def test_enum(self, pseudo_type):
        assert issubclass(type(pseudo_type), Enum)


class TestEquality:
    def test_int(self, node_id):
        assert node_id == 123
        assert node_id != 321

    def test_float(self, timestamp):
        assert timestamp == 9.123
        assert timestamp != 2

    def test_string(self, style_sheet_id):
        assert style_sheet_id == "c001"
        assert style_sheet_id != "helloworld"

    def test_list_of_builtins(self, quad):
        assert quad == [3, 2, 1]

    def test_enum(self, pseudo_type):
        assert pseudo_type == cdpy.dom.PseudoType.BEFORE


class TestStr:
    def test_int(self, node_id):
        assert str(node_id) == "NodeId(123)"

    def test_float(self, timestamp):
        assert str(timestamp) == "Timestamp(9.123)"

    def test_string(self, style_sheet_id):
        assert str(style_sheet_id) == "c001"

    def test_list_of_builtins(self, quad):
        assert str(quad) == "Quad([3, 2, 1])"

    def test_enum(self, pseudo_type):
        assert str(pseudo_type) == "PseudoType.BEFORE"


class TestRepr:
    def test_int(self, node_id):
        assert repr(node_id) == "NodeId(123)"

    def test_float(self, timestamp):
        assert repr(timestamp) == "Timestamp(9.123)"

    def test_string(self, style_sheet_id):
        assert repr(style_sheet_id) == "StyleSheetId('c001')"

    def test_list_of_builtins(self, quad):
        assert repr(quad) == "Quad([3, 2, 1])"

    def test_enum(self, pseudo_type):
        assert str(pseudo_type) == "PseudoType.BEFORE"


class TestAddition:
    def test_int(self, node_id):
        assert node_id + 5 == 128

    def test_float(self, timestamp):
        assert timestamp + 1.12 == approx(10.135, 0.02)


class TestConcatenation:
    def test_string(self, style_sheet_id):
        assert style_sheet_id + "hello" == "c001hello"

    def test_list_of_builtins(self, quad):
        assert quad + [4, 5] == [3, 2, 1, 4, 5]
