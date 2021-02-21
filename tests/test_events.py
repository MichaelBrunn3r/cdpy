import pytest

from cdpy import cdp


class TestFromJson:
    def test_builtin(self):
        e = cdp.animation.AnimationCanceled.from_json({"id": "someid"})

        assert type(e) == cdp.animation.AnimationCanceled
        assert e.id == "someid"

    def test_simple(self):
        e = cdp.application_cache.ApplicationCacheStatusUpdated.from_json(
            {"frameId": "someid", "manifestURL": "url", "status": 42}
        )

        assert type(e) == cdp.application_cache.ApplicationCacheStatusUpdated
        assert type(e.frameId) == cdp.page.FrameId
        assert e.frameId == "someid"

    def test_object(self):
        e = cdp.audits.IssueAdded.from_json(
            {"issue": {"code": "HeavyAdIssue", "details": {}}}
        )

        assert type(e) == cdp.audits.IssueAdded
        assert type(e.issue) == cdp.audits.InspectorIssue
        assert type(e.issue.code) == cdp.audits.InspectorIssueCode
        assert type(e.issue.details) == cdp.audits.InspectorIssueDetails

    def test_object_list(self):
        e = cdp.cast.SinksUpdated.from_json(
            {"sinks": [{"name": "a", "id": "ida"}, {"name": "b", "id": "idb"}]}
        )

        assert type(e) == cdp.cast.SinksUpdated
        assert len(e.sinks) == 2
        assert type(e.sinks[0]) == cdp.cast.Sink
        assert type(e.sinks[1]) == cdp.cast.Sink
        assert e.sinks[0].name == "a"
        assert e.sinks[1].name == "b"
