from dataclasses import is_dataclass
from typing import List

import pytest

import cdpy


@pytest.fixture
def required_node_args():
    return {
        "nodeId": 222,
        "backendNodeId": 333,
        "nodeType": 7,
        "nodeName": "nname",
        "localName": "lname",
        "nodeValue": "nval",
    }


@pytest.fixture
def required_node_args2():
    return {
        "nodeId": 721,
        "backendNodeId": 331,
        "nodeType": 7,
        "nodeName": "nname",
        "localName": "lname",
        "nodeValue": "nval",
    }


@pytest.fixture
def required_node_args3():
    return {
        "nodeId": 111,
        "backendNodeId": 2,
        "nodeType": 7,
        "nodeName": "nname",
        "localName": "lname",
        "nodeValue": "nval",
    }


@pytest.fixture
def node(required_node_args):
    return cdpy.dom.Node(**required_node_args)


class TestFromJson:
    def test_builtin_arg(self, required_node_args):
        node = cdpy.dom.Node.from_json(required_node_args)

        assert type(node.nodeType) == int
        assert node.nodeType == 7

    def test_builtin_list_arg(self, required_node_args):
        args = required_node_args | {"attributes": ["a", "b", "c"]}
        node = cdpy.dom.Node.from_json(args)

        assert node.attributes
        assert type(node.attributes) == list
        assert node.attributes == ["a", "b", "c"]

    def test_typeless_enum_arg(self):
        args = {"text": "lorem", "source": "mediaRule"}
        media = cdpy.css.CSSMedia.from_json(args)

        assert type(media.source) == str
        assert media.source == "mediaRule"

    def test_simple_arg(self, required_node_args):
        node = cdpy.dom.Node.from_json(required_node_args)

        assert type(node.nodeId) == cdpy.dom.NodeId
        assert node.nodeId == 222

    def test_simple_list_arg(self):
        args = {"index": [1, 2], "value": [1, 2]}
        rsd = cdpy.dom_snapshot.RareStringData.from_json(args)

        assert type(rsd.value) == list
        assert type(rsd.value[0]) == cdpy.dom_snapshot.StringIndex
        assert rsd.value == [
            cdpy.dom_snapshot.StringIndex(1),
            cdpy.dom_snapshot.StringIndex(2),
        ]

    def test_enum_arg(self, required_node_args):
        args = required_node_args | {"pseudoType": "marker"}
        node = cdpy.dom.Node.from_json(args)

        assert type(node.pseudoType) == cdpy.dom.PseudoType
        assert node.pseudoType == cdpy.dom.PseudoType.MARKER

    def test_enum_list_arg(self):
        args = {
            "blockedReasons": ["UserPreferences", "UnknownError"],
            "cookieLine": "lorem",
        }
        bscwr = cdpy.network.BlockedSetCookieWithReason.from_json(args)

        assert type(bscwr.blockedReasons) == list
        assert type(bscwr.blockedReasons[0]) == cdpy.network.SetCookieBlockedReason
        assert bscwr.blockedReasons == [
            cdpy.network.SetCookieBlockedReason.USER_PREFERENCES,
            cdpy.network.SetCookieBlockedReason.UNKNOWN_ERROR,
        ]

    def test_object_arg(self, required_node_args, required_node_args2):
        args = required_node_args | {"contentDocument": required_node_args2}
        nested_node = cdpy.dom.Node.from_json(required_node_args2)
        node = cdpy.dom.Node.from_json(args)

        assert type(node.contentDocument) == cdpy.dom.Node
        assert node.contentDocument == nested_node

    def test_object_list_arg(
        self, required_node_args, required_node_args2, required_node_args3
    ):
        nested_node_1 = cdpy.dom.Node(**required_node_args2)
        nested_node_2 = cdpy.dom.Node(**required_node_args3)
        args = required_node_args | {
            "children": [required_node_args2, required_node_args3]
        }
        node = cdpy.dom.Node.from_json(args)

        assert type(node.children) == list
        assert node.children == [nested_node_1, nested_node_2]

    def test_optional_args_default_to_none(self):
        style = cdpy.css.CSSStyle.from_json(
            {"cssProperties": [], "shorthandEntries": []}
        )

        assert style.cssProperties == []
        assert style.shorthandEntries == []
        assert style.cssText == None
        assert style.range == None

    def test_forget_required_arg(self):
        args = {
            "nodeId": 222,
            "backendNodeId": 333,
            "nodeType": 7,
            # "nodeName": "nname", <- forgot
            "localName": "lname",
            "nodeValue": "nval",
        }

        with pytest.raises(KeyError):
            cdpy.dom.Node.from_json(args)

    def test_forget_required_but_pass_optional(self):
        args = {
            "nodeId": 222,
            "backendNodeId": 333,
            "nodeType": 7,
            # "nodeName": "nname", <- forgot
            "localName": "lname",
            "nodeValue": "nval",
            "childNodeCount": 10,  # <- optional
        }

        with pytest.raises(KeyError):
            cdpy.dom.Node.from_json(args)

    def test_unordered_args(self):
        args = {
            "nodeValue": "nval",
            "nodeId": 222,
            "localName": "lname",
            "nodeType": 7,
            "childNodeCount": 10,
            "backendNodeId": 333,
            "nodeName": "nname",
        }
        node = cdpy.dom.Node.from_json(args)

        assert node.nodeId == 222
        assert node.backendNodeId == 333
        assert node.nodeType == 7
        assert node.nodeName == "nname"
        assert node.localName == "lname"
        assert node.nodeValue == "nval"
        assert node.childNodeCount == 10

    def test_type_from_other_domain(self, required_node_args):
        args = required_node_args | {"frameId": "deadbeef"}
        node = cdpy.dom.Node.from_json(args)

        assert node.frameId == "deadbeef"
        assert type(node.frameId) == cdpy.page.FrameId


class TestToJson:
    def test_builtin_attr(self, node):
        json = node.to_json()

        assert "nodeId" in json
        assert type(json["nodeId"]) == int

    def test_builtin_list_attr(self, node):
        node.attributes = ["a", "b", "c"]
        json = node.to_json()

        assert "attributes" in json
        assert type(json["attributes"]) == list
        assert json["attributes"] == ["a", "b", "c"]

    def test_typeless_enum_attr(self):
        args = {"text": "lorem", "source": "mediaRule"}
        json = cdpy.css.CSSMedia.from_json(args).to_json()

        assert "source" in json
        assert type(json["source"]) == str
        assert json["source"] == "mediaRule"
        assert json == args

    def test_simple_attr(self, required_node_args):
        json = cdpy.dom.Node.from_json(required_node_args).to_json()

        assert "nodeId" in json
        assert type(json["nodeId"]) == int
        assert json["nodeId"] == 222
        assert json == required_node_args

    def test_simple_list_attr(self):
        args = {"index": [1, 2], "value": [1, 2]}
        json = cdpy.dom_snapshot.RareStringData.from_json(args).to_json()

        assert "value" in json
        assert type(json["value"]) == list
        assert type(json["value"][0]) == int
        assert json["value"] == [1, 2]
        assert json == args

    def test_enum_attr(self, required_node_args):
        args = required_node_args | {"pseudoType": "marker"}
        json = cdpy.dom.Node.from_json(args).to_json()

        assert "pseudoType" in json
        assert type(json["pseudoType"]) == str
        assert json["pseudoType"] == "marker"
        assert json == args

    def test_enum_list_attr(self):
        args = {
            "blockedReasons": ["UserPreferences", "UnknownError"],
            "cookieLine": "lorem",
        }
        json = cdpy.network.BlockedSetCookieWithReason.from_json(args).to_json()

        assert "blockedReasons" in json
        assert type(json["blockedReasons"]) == list
        assert type(json["blockedReasons"][0]) == str
        assert json["blockedReasons"] == ["UserPreferences", "UnknownError"]
        assert json == args

    def test_object_attr(self, required_node_args, required_node_args2):
        args = required_node_args | {"contentDocument": required_node_args2}
        nested_node = cdpy.dom.Node.from_json(required_node_args2)
        json = cdpy.dom.Node.from_json(args).to_json()

        assert "contentDocument" in json
        assert type(json["contentDocument"]) == dict
        assert json["contentDocument"] == required_node_args2
        assert json == args

    def test_object_list_attr(
        self, required_node_args, required_node_args2, required_node_args3
    ):
        nested_node_1 = cdpy.dom.Node(**required_node_args2)
        nested_node_2 = cdpy.dom.Node(**required_node_args3)
        args = required_node_args | {
            "children": [required_node_args2, required_node_args3]
        }
        json = cdpy.dom.Node.from_json(args).to_json()

        assert "children" in json
        assert type(json["children"]) == list
        assert json["children"] == [required_node_args2, required_node_args3]
        assert json == args

    def test_unset_attributes_are_filtered(self, required_node_args):
        node = cdpy.dom.Node.from_json(required_node_args)
        json = node.to_json()

        for attr in node.__dict__:
            if getattr(node, attr) == None:
                assert attr not in json

    def test_type_from_other_domain(self, required_node_args):
        args = required_node_args | {"frameId": "deadbeef"}
        json = cdpy.dom.Node.from_json(args).to_json()

        assert "frameId" in json
        assert type(json["frameId"]) == str
        assert json["frameId"] == "deadbeef"
        assert json == args
