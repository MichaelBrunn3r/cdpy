import pytest
from requests.exceptions import InvalidURL

import cdpy


class TestGetTargets:
    @pytest.fixture
    def response(self):
        return [
            {
                "description": "",
                "devtoolsFrontendUrl": "/devtools/inspector.html?ws=127.0.0.1:9222/devtools/page/18BC9EFA11A74748F976B4821CB65FE0",
                "id": "18BC9EFA11A74748F976B4821CB65FE0",
                "title": "127.0.0.1:9222/json",
                "type": "page",
                "url": "http://127.0.0.1:9222/json/list",
                "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/page/18BC9EFA11A74748F976B4821CB65FE0",
            },
            {
                "description": "",
                "devtoolsFrontendUrl": "/devtools/inspector.html?ws=127.0.0.1:9222/devtools/page/0DBE8C9E353ACC65A88F4A9725CCAC21",
                "id": "0DBE8C9E353ACC65A88F4A9725CCAC21",
                "title": "Neuer Tab",
                "type": "page",
                "url": "chrome://newtab/",
                "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/page/0DBE8C9E353ACC65A88F4A9725CCAC21",
            },
            {
                "description": "",
                "devtoolsFrontendUrl": "/devtools/inspector.html?ws=127.0.0.1:9222/devtools/page/2EC6F24EE37CC20CA22AD084DCD7821B",
                "id": "2EC6F24EE37CC20CA22AD084DCD7821B",
                "parentId": "0DBE8C9E353ACC65A88F4A9725CCAC21",
                "title": "chrome-untrusted://new-tab-page/custom_background_image?url=",
                "type": "iframe",
                "url": "chrome-untrusted://new-tab-page/custom_background_image?url=",
                "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/page/2EC6F24EE37CC20CA22AD084DCD7821B",
            },
            {
                "description": "",
                "devtoolsFrontendUrl": "/devtools/inspector.html?ws=127.0.0.1:9222/devtools/page/C47106201278C5935BE059619B9170BA",
                "id": "C47106201278C5935BE059619B9170BA",
                "parentId": "0DBE8C9E353ACC65A88F4A9725CCAC21",
                "title": "chrome-untrusted://new-tab-page/one-google-bar?paramsencoded=",
                "type": "iframe",
                "url": "chrome-untrusted://new-tab-page/one-google-bar?paramsencoded=",
                "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/page/C47106201278C5935BE059619B9170BA",
            },
            {
                "description": "",
                "devtoolsFrontendUrl": "/devtools/inspector.html?ws=127.0.0.1:9222/devtools/page/B852563EAE35B37EC9A59A9629B68E2A",
                "id": "B852563EAE35B37EC9A59A9629B68E2A",
                "parentId": "0DBE8C9E353ACC65A88F4A9725CCAC21",
                "title": "https://www.google.com/?fpdoodle=1&amp;doodle=174786609&amp;ntp=2&amp;theme_messages=0&amp;nord=1",
                "type": "iframe",
                "url": "https://www.google.com/?fpdoodle=1&doodle=174786609&ntp=2&theme_messages=0&nord=1",
                "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/page/B852563EAE35B37EC9A59A9629B68E2A",
            },
        ]

    def test_endpoint_url(self, response):
        def check_url(url: str):
            assert url == "http://127.0.0.1:9222/json/list"
            return response

        cdpy.get_targets("http://127.0.0.1:9222", check_url)

    def test_invalid_url(self):
        def request_targets(url: str):
            raise InvalidURL()

        with pytest.raises(InvalidURL):
            cdpy.get_targets("http://127.0.0.1:9222", request_targets)

    def test_parse_target(self, response):
        targets = list(cdpy.get_targets("http://127.0.0.1:9222", lambda url: response))

        assert len(targets) == 5
        assert type(targets[0]) == cdpy.Target
        assert targets[0].type == cdpy.TargetType.PAGE
        assert type(targets[2]) == cdpy.Target
        assert targets[2].type == cdpy.TargetType.IFRAME

    def test_filter_targets(self, response):
        pages = list(
            cdpy.get_targets(
                "http://127.0.0.1:9222", lambda url: response, [cdpy.TargetType.PAGE]
            )
        )

        assert len(pages) == 2
        assert pages[0].type == cdpy.TargetType.PAGE
        assert pages[1].type == cdpy.TargetType.PAGE
