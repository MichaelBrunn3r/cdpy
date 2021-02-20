import pytest

import cdpy


class TestFromJson:
    def test_builtin(self):
        e = cdpy.animation.AnimationCanceled.from_json({"id": "someid"})

        assert type(e) == cdpy.animation.AnimationCanceled
        assert e.id == "someid"

    def test_simple(self):
        e = cdpy.application_cache.ApplicationCacheStatusUpdated.from_json(
            {"frameId": "someid", "manifestURL": "url", "status": 42}
        )

        assert type(e) == cdpy.application_cache.ApplicationCacheStatusUpdated
        assert type(e.frameId) == cdpy.page.FrameId
        assert e.frameId == "someid"

    def test_object(self):
        e = cdpy.audits.IssueAdded.from_json(
            {"issue": {"code": "HeavyAdIssue", "details": {}}}
        )

        assert type(e) == cdpy.audits.IssueAdded
        assert type(e.issue) == cdpy.audits.InspectorIssue
        assert type(e.issue.code) == cdpy.audits.InspectorIssueCode
        assert type(e.issue.details) == cdpy.audits.InspectorIssueDetails

    def test_object_list(self):
        e = cdpy.cast.SinksUpdated.from_json(
            {"sinks": [{"name": "a", "id": "ida"}, {"name": "b", "id": "idb"}]}
        )

        assert type(e) == cdpy.cast.SinksUpdated
        assert len(e.sinks) == 2
        assert type(e.sinks[0]) == cdpy.cast.Sink
        assert type(e.sinks[1]) == cdpy.cast.Sink
        assert e.sinks[0].name == "a"
        assert e.sinks[1].name == "b"
