import pytest
from pytest import approx

import cdpy


class TestInt:
    @pytest.fixture
    def node_id(self):
        return cdpy.dom.NodeId(123)

    def test_str(self, node_id):
        assert str(node_id) == "NodeId(123)"

    def test_repr(self, node_id):
        assert repr(node_id) == "NodeId(123)"

    def test_equality(self, node_id):
        assert node_id == 123
        assert node_id != 321

    def test_addition(self, node_id):
        assert node_id + 5 == 128


class TestFloat:
    @pytest.fixture
    def timestamp(self):
        return cdpy.runtime.Timestamp(9.123)

    def test_str(self, timestamp):
        assert str(timestamp) == "Timestamp(9.123)"

    def test_repr(self, timestamp):
        assert repr(timestamp) == "Timestamp(9.123)"

    def test_equality(self, timestamp):
        assert timestamp == 9.123
        assert timestamp != 2

    def test_addition(self, timestamp):
        assert timestamp + 1.12 == approx(10.135, 0.02)


class TestString:
    @pytest.fixture
    def style_sheet_id(self):
        return cdpy.css.StyleSheetId("c001")

    def test_str(self, style_sheet_id):
        assert str(style_sheet_id) == "c001"

    def test_repr(self, style_sheet_id):
        assert repr(style_sheet_id) == "StyleSheetId('c001')"

    def test_equality(self, style_sheet_id):
        assert style_sheet_id == "c001"
        assert style_sheet_id != "helloworld"

    def test_concatenation(self, style_sheet_id):
        assert style_sheet_id + "hello" == "c001hello"


class TestList:
    @pytest.fixture
    def quad(self):
        return cdpy.dom.Quad([3, 2, 1])

    def test_str(self, quad):
        assert str(quad) == "Quad([3, 2, 1])"

    def test_repr(self, quad):
        assert repr(quad) == "Quad([3, 2, 1])"

    def test_equality(self, quad):
        assert quad == [3, 2, 1]

    def test_append(self, quad):
        quad.append(4)
        assert quad == [3, 2, 1, 4]

    def test_concatenation(self, quad):
        assert quad + [4, 5] == [3, 2, 1, 4, 5]

    def test_slice(self, quad):
        assert quad[1] == 2
        assert quad[-1] == 1
        assert quad[1:] == [2, 1]
        assert quad[:2] == [3, 2]
