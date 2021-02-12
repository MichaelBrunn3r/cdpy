from typing import Generator

import cdpy


class TestUnparseTypes:
    def test_unparse_builtin_list(self):
        args = {"nodeId": cdpy.dom.NodeId(321), "forcedPseudoClasses": ["a", "b", "c"]}
        expected = {
            "method": "CSS.forcePseudoState",
            "params": {"nodeId": 321, "forcedPseudoClasses": ["a", "b", "c"]},
        }
        r = cdpy.css.force_pseudo_state(**args)

        assert "params" in r
        assert "forcedPseudoClasses" in r["params"]
        forcedPseudoClasses = r["params"]["forcedPseudoClasses"]
        assert type(forcedPseudoClasses) == list
        assert type(forcedPseudoClasses[0]) == str
        assert forcedPseudoClasses[0] == "a"
        assert r == expected

    def test_unparse_typeless_enum(self):
        args = {
            "transferMode": "somemode",
        }
        expected = {"method": "Tracing.start", "params": {"transferMode": "somemode"}}
        r = cdpy.tracing.start(**args)

        assert r == expected

    def test_unparse_simple(self):
        args = {"nodeId": cdpy.dom.NodeId(123), "name": "aname", "value": "avalue"}
        expected = {
            "method": "DOM.setAttributeValue",
            "params": {"nodeId": 123, "name": "aname", "value": "avalue"},
        }
        r = cdpy.dom.set_attribute_value(**args)

        assert "params" in r
        assert "nodeId" in r["params"]
        assert type(r["params"]["nodeId"]) == int
        assert r["params"]["nodeId"] == 123
        assert r == expected

    def test_unparse_simple_list(self):
        args = {"nodeIds": [cdpy.dom.NodeId(222), cdpy.dom.NodeId(333)]}
        expected = {
            "method": "Overlay.getGridHighlightObjectsForTest",
            "params": {"nodeIds": [222, 333]},
        }
        r = cdpy.overlay.get_grid_highlight_objects_for_test(**args)

        assert "params" in r
        assert "nodeIds" in r["params"]
        nodeIds = r["params"]["nodeIds"]
        assert type(nodeIds) == list
        assert type(nodeIds[0]) == int
        assert nodeIds == [222, 333]
        assert r == expected

    def test_unparse_enum(self):
        args = {"service": cdpy.background_service.ServiceName.BACKGROUND_SYNC}
        expected = {
            "method": "BackgroundService.startObserving",
            "params": {"service": "backgroundSync"},
        }
        r = cdpy.background_service.start_observing(**args)

        assert "params" in r
        assert "service" in r["params"]
        assert type(r["params"]["service"]) == str
        assert r["params"]["service"] == "backgroundSync"
        assert r == expected

    def test_unparse_enum_list(self):
        args = {
            "permissions": [
                cdpy.browser.PermissionType.GEOLOCATION,
                cdpy.browser.PermissionType.NFC,
            ]
        }
        expected = {
            "method": "Browser.grantPermissions",
            "params": {"permissions": ["geolocation", "nfc"]},
        }
        r = cdpy.browser.grant_permissions(**args)

        assert "params" in r
        assert "permissions" in r["params"]
        permissions = r["params"]["permissions"]
        assert type(permissions) == list
        assert type(permissions[0]) == str
        assert permissions[0] == "geolocation"
        assert r == expected

    def test_unparse_object(self):
        args = {
            "styleSheetId": cdpy.css.StyleSheetId("someid"),
            "ruleText": "arule",
            "location": cdpy.css.SourceRange(3, 0, 4, 5),
        }
        expected = {
            "method": "CSS.addRule",
            "params": {
                "styleSheetId": "someid",
                "ruleText": "arule",
                "location": {
                    "startLine": 3,
                    "startColumn": 0,
                    "endLine": 4,
                    "endColumn": 5,
                },
            },
        }
        r = cdpy.css.add_rule(**args)

        assert "params" in r
        assert "location" in r["params"]
        location = r["params"]["location"]
        assert type(location) == dict
        assert type(location["startLine"]) == int
        assert location["startLine"] == 3
        assert r == expected

    def test_unparse_object_list(self):
        args = {
            "propertiesToTrack": [
                cdpy.css.CSSComputedStyleProperty("a", "vala"),
                cdpy.css.CSSComputedStyleProperty("b", "valb"),
            ]
        }
        expected = {
            "method": "CSS.trackComputedStyleUpdates",
            "params": {
                "propertiesToTrack": [
                    {"name": "a", "value": "vala"},
                    {"name": "b", "value": "valb"},
                ]
            },
        }
        r = cdpy.css.track_computed_style_updates(**args)

        assert "params" in r
        assert "propertiesToTrack" in r["params"]
        propertiesToTrack = r["params"]["propertiesToTrack"]
        assert type(propertiesToTrack) == list
        assert type(propertiesToTrack[0]) == dict
        assert propertiesToTrack[0] == {"name": "a", "value": "vala"}
        assert r == expected
