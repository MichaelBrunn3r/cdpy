from dataclasses import is_dataclass
from typing import List

import pytest

import cdpy


def assert_attributes_have_value(it, attributes: dict):
    """Assert the value of the specified attributes in `it`"""
    for name, value in attributes.items():
        assert hasattr(it, name)
        assert getattr(it, name) == value


def assert_attributes_have_type(it, attributes: dict):
    """Assert the type of the specified attributes in `it`"""
    for attr, expected_type in attributes.items():
        assert hasattr(it, attr)
        assert type(getattr(it, attr)) == expected_type


def assert_other_attributes_have_value(it, attributes: List[str], expected_value):
    """Assert that all dataclass attributes not in the list have some value"""
    assert is_dataclass(it)
    for attr in it.__dataclass_fields__:
        if attr not in attributes:
            assert getattr(it, attr) == expected_value


class TestFromJson:
    @pytest.fixture
    def required_node_args(self):
        return {
            "nodeId": 222,
            "backendNodeId": 333,
            "nodeType": 7,
            "nodeName": "nname",
            "localName": "lname",
            "nodeValue": "nval",
        }

    def test_pass_required_args(self, required_node_args):
        node = cdpy.dom.Node.from_json(required_node_args)

        assert_attributes_have_value(node, required_node_args)
        assert_attributes_have_type(
            node,
            {
                "nodeId": cdpy.dom.NodeId,
                "backendNodeId": cdpy.dom.BackendNodeId,
                "nodeType": int,
                "nodeName": str,
                "localName": str,
                "nodeValue": str,
            },
        )
        assert_other_attributes_have_value(node, required_node_args.keys(), None)

    def test_forget_one_required_arg(self, required_node_args):
        for arg in required_node_args:
            with pytest.raises(Exception, match=f".*{arg}.*"):
                json = required_node_args.copy()
                del json[arg]
                cdpy.dom.Node.from_json(json)

    def test_pass_optional_instead_of_required_arg(self, required_node_args):
        del required_node_args["nodeValue"]
        required_node_args["hello"] = "world"

        with pytest.raises(Exception, match=".*nodeValue.*"):
            cdpy.dom.Node.from_json(required_node_args)

    def test_pass_list_arg(self, required_node_args):
        args = required_node_args | {"attributes": ["attr1", "val1", "attr2", "val2"]}
        node = cdpy.dom.Node.from_json(args)

        assert node.attributes == ["attr1", "val1", "attr2", "val2"]

    def test_pass_optional_arg(self, required_node_args):
        args = {**required_node_args, "childNodeCount": 123}
        node = cdpy.dom.Node.from_json(args)

        assert node.childNodeCount == 123


# def test_nested_from_json():
#     # 1. Correctly parse list attributes
#     json = {'content': [1,2,3,4], 'padding': [5,6,7,8], 'border': [9,10,11,12], 'margin': [13,14,15,16], 'width': 10, 'height': 5}
#     box_model = cdpy.dom.BoxModel.from_json(json)

#     assert_attributes_have_value(box_model, json)
#     assert_attributes_have_type(box_model, {'content': cdpy.dom.Quad, 'padding': cdpy.dom.Quad, 'border': cdpy.dom.Quad, 'margin': cdpy.dom.Quad, 'width': int, 'height': int})

#     # 2. Parse Enum
#     json = {'nodeId': 222, 'backendNodeId': 333, 'nodeType': 7, 'nodeName': 'nname', 'localName': 'lname', 'nodeValue': 'nval'}
#     node = cdpy.dom.Node.from_json(json)
