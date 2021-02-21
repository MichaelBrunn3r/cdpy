from typing import Generator

import pytest

from cdpy import cdp


def execute_and_assert_yield(method, expected_yield):
    method_json = method.send(None)

    assert method_json == expected_yield
    return method


class TestCreateJson:
    def test_builtin_list(self):
        args = {"nodeId": cdp.dom.NodeId(321), "forcedPseudoClasses": ["a", "b", "c"]}
        expected = {
            "method": "CSS.forcePseudoState",
            "params": {"nodeId": 321, "forcedPseudoClasses": ["a", "b", "c"]},
        }
        r = cdp.css.force_pseudo_state(**args)

        assert "params" in r
        assert "forcedPseudoClasses" in r["params"]
        forcedPseudoClasses = r["params"]["forcedPseudoClasses"]
        assert type(forcedPseudoClasses) == list
        assert type(forcedPseudoClasses[0]) == str
        assert forcedPseudoClasses[0] == "a"
        assert r == expected

    def test_typeless_enum(self):
        args = {
            "transferMode": "somemode",
        }
        expected = {"method": "Tracing.start", "params": {"transferMode": "somemode"}}
        r = cdp.tracing.start(**args)

        assert r == expected

    def test_unparse_simple(self):
        args = {"nodeId": cdp.dom.NodeId(123), "name": "aname", "value": "avalue"}
        expected = {
            "method": "DOM.setAttributeValue",
            "params": {"nodeId": 123, "name": "aname", "value": "avalue"},
        }
        r = cdp.dom.set_attribute_value(**args)

        assert "params" in r
        assert "nodeId" in r["params"]
        assert type(r["params"]["nodeId"]) == int
        assert r["params"]["nodeId"] == 123
        assert r == expected

    def test_simple_list(self):
        args = {"nodeIds": [cdp.dom.NodeId(222), cdp.dom.NodeId(333)]}
        expected = {
            "method": "Overlay.getGridHighlightObjectsForTest",
            "params": {"nodeIds": [222, 333]},
        }
        r = cdp.overlay.get_grid_highlight_objects_for_test(**args)

        assert issubclass(type(r), Generator)
        r = next(r)
        assert "params" in r
        assert "nodeIds" in r["params"]
        nodeIds = r["params"]["nodeIds"]
        assert type(nodeIds) == list
        assert type(nodeIds[0]) == int
        assert nodeIds == [222, 333]
        assert r == expected

    def test_enum(self):
        args = {"service": cdp.background_service.ServiceName.BACKGROUND_SYNC}
        expected = {
            "method": "BackgroundService.startObserving",
            "params": {"service": "backgroundSync"},
        }
        r = cdp.background_service.start_observing(**args)

        assert "params" in r
        assert "service" in r["params"]
        assert type(r["params"]["service"]) == str
        assert r["params"]["service"] == "backgroundSync"
        assert r == expected

    def test_enum_list(self):
        args = {
            "permissions": [
                cdp.browser.PermissionType.GEOLOCATION,
                cdp.browser.PermissionType.NFC,
            ]
        }
        expected = {
            "method": "Browser.grantPermissions",
            "params": {"permissions": ["geolocation", "nfc"]},
        }
        r = cdp.browser.grant_permissions(**args)

        assert "params" in r
        assert "permissions" in r["params"]
        permissions = r["params"]["permissions"]
        assert type(permissions) == list
        assert type(permissions[0]) == str
        assert permissions[0] == "geolocation"
        assert r == expected

    def test_object(self):
        args = {
            "styleSheetId": cdp.css.StyleSheetId("someid"),
            "ruleText": "arule",
            "location": cdp.css.SourceRange(3, 0, 4, 5),
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
        r = cdp.css.add_rule(**args)

        assert issubclass(type(r), Generator)
        r = next(r)
        assert "params" in r
        assert "location" in r["params"]
        location = r["params"]["location"]
        assert type(location) == dict
        assert type(location["startLine"]) == int
        assert location["startLine"] == 3
        assert r == expected

    def test_object_list(self):
        args = {
            "propertiesToTrack": [
                cdp.css.CSSComputedStyleProperty("a", "vala"),
                cdp.css.CSSComputedStyleProperty("b", "valb"),
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
        r = cdp.css.track_computed_style_updates(**args)

        assert "params" in r
        assert "propertiesToTrack" in r["params"]
        propertiesToTrack = r["params"]["propertiesToTrack"]
        assert type(propertiesToTrack) == list
        assert type(propertiesToTrack[0]) == dict
        assert propertiesToTrack[0] == {"name": "a", "value": "vala"}
        assert r == expected


class TestReturn:
    @pytest.fixture
    def executed_add_script_method(self):
        return execute_and_assert_yield(
            cdp.page.add_script_to_evaluate_on_load("abcdef"),
            {
                "method": "Page.addScriptToEvaluateOnLoad",
                "params": {"scriptSource": "abcdef"},
            },
        )

    @pytest.fixture
    def executed_installability_errors_method(self):
        return execute_and_assert_yield(
            cdp.page.get_installability_errors(),
            {"method": "Page.getInstallabilityErrors", "params": {}},
        )

    @pytest.fixture
    def executed_get_frame_tree_method(self):
        return execute_and_assert_yield(
            cdp.page.get_frame_tree(), {"method": "Page.getFrameTree", "params": {}}
        )

    @pytest.fixture
    def executed_capture_screenshot_method(self):
        return execute_and_assert_yield(
            cdp.page.capture_screenshot(),
            {"method": "Page.captureScreenshot", "params": {}},
        )

    @pytest.fixture
    def executed_get_resource_content(self):
        return execute_and_assert_yield(
            cdp.page.get_resource_content(cdp.page.FrameId(22), "url"),
            {
                "method": "Page.getResourceContent",
                "params": {"frameId": "22", "url": "url"},
            },
        )

    def test_builtin(self, executed_capture_screenshot_method):
        response_json = {"id": 432, "data": "some-data"}

        with pytest.raises(StopIteration):
            response = executed_capture_screenshot_method.send(response_json)

            assert type(response) == str
            assert response == "some-data"

    @pytest.mark.filterwarnings("ignore:Call to deprecated function")
    def test_simple(self, executed_add_script_method):
        response_json = {"id": 87634, "identifier": "anidentfier"}

        with pytest.raises(StopIteration):
            response = executed_add_script_method.send(response_json)

            assert type(response) == cdp.page.ScriptIdentifier
            assert response == "anidentfier"

    def test_object(self, executed_get_frame_tree_method):
        response_json = {
            "id": 11,
            "frameTree": {
                "frame": {
                    "id": 123,
                    "loaderId": 2,
                    "url": "...",
                    "domainAndRegistry": "...",
                    "securityOrigin": "...",
                    "mimeType": "...",
                    "secureContextType": "Secure",
                    "crossOriginIsolatedContextType": "Isolated",
                    "gatedAPIFeatures": [],
                }
            },
        }

        with pytest.raises(StopIteration):
            response = executed_get_frame_tree_method.send(response_json)

            assert type(response) == cdp.page.FrameTree
            assert response.frame.id == 123

    def test_list_of_objects(self, executed_installability_errors_method):
        response_json = {
            "id": 10,
            "installabilityErrors": [
                {
                    "errorId": 1,
                    "errorArguments": [
                        {"name": "minimum-icon-size-in-pixels", "value": 64}
                    ],
                },
                {"errorId": 5, "errorArguments": []},
            ],
        }

        with pytest.raises(StopIteration):
            response = executed_installability_errors_method.send(response_json)

            assert type(response) == list
            assert len(response) == 2
            assert type(response[0]) == cdp.page.InstallabilityError
            assert response[0].errorId == 1
            assert type(response[1]) == cdp.page.InstallabilityError
            assert response[1].errorId == 5

    def test_return_multiple(self, executed_get_resource_content):
        response_json = {"content": "lorem", "base64Encoded": False}

        with pytest.raises(StopIteration):
            response = executed_get_resource_content.send(response_json)

            assert type(response) == dict
            assert "content" in response
            assert response["content"] == "lorem"
            assert "base64Encoded" in response
            assert response["base64Encoded"] == False

    @pytest.mark.filterwarnings("ignore:Call to deprecated function")
    def test_send_empty_response(self, executed_add_script_method):
        with pytest.raises(KeyError, match=".*identifier.*"):
            response = executed_add_script_method.send({})

    @pytest.mark.filterwarnings("ignore:Call to deprecated function")
    def test_send_response_without_id(self, executed_add_script_method):
        response_json = {"identifier": "anidentfier"}

        with pytest.raises(StopIteration):
            response = executed_add_script_method.send(response_json)

            assert type(response) == cdp.page.ScriptIdentifier
            assert response == "anidentfier"


class TestMisc:
    def test_deprecation_warning(self):
        with pytest.deprecated_call():
            cdp.page.add_script_to_evaluate_on_load("abcdef")
