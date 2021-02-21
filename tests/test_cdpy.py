import pytest

import cdpy


class TestParseEvent:
    def test_response_without_method_name(self):
        with pytest.raises(cdpy.EventParserError, match=".*method.*"):
            cdpy.parse_event({"params": {}})

    def test_response_without_params(self):
        with pytest.raises(cdpy.EventParserError, match=".*params.*"):
            cdpy.parse_event({"method": "acb"})

    def test_unknown_event(self):
        with pytest.raises(cdpy.EventParserError, match=".*parser for event.*"):
            cdpy.parse_event({"method": "lorem", "params": {}})

    def test_valid_event(self):
        e = cdpy.parse_event(
            {
                "method": "Audits.issueAdded",
                "params": {"issue": {"code": "HeavyAdIssue", "details": {}}},
            }
        )

        assert type(e) == cdpy.audits.IssueAdded
