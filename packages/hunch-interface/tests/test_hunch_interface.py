import json
from pathlib import Path

import pytest

from hunch_adapter import EmotionClaimError, HunchProvider, MockHunchProvider, assert_no_emotion_claims
from hunch_adapter.worker import main as worker_main, mock_result

RULE = {"id": "rule-1", "kind": "user_rule", "when": "afternoon", "intent": "calmer", "text": "calmer in afternoon sun"}


def test_mock_satisfies_protocol():
    assert isinstance(MockHunchProvider(), HunchProvider)


def test_sources_rule_inferred_guess():
    h = MockHunchProvider()
    obs = h.observe({"time_of_day": "afternoon", "sunlit_fraction": 0.5})
    g = h.propose_goal(obs, [RULE])
    assert g["source"] == "user_rule" and g["provider"]["mock"] and g["user_preferences_used"] == ["rule-1"]
    g2 = h.propose_goal(obs, [])
    assert g2["source"] == "model_guess" and g2["uncertainty"] > 0.5
    h.record_feedback({"intent": "calmer", "rating": 1})
    h.record_feedback({"intent": "calmer", "rating": 1})
    assert h.propose_goal(obs, [])["source"] == "inferred_preference"
    assert all(o["mock"] for o in obs)


@pytest.mark.parametrize("text", [
    "hunch detects your emotions", "we read their mood from the camera", "emotion detection enabled",
    "you feel anxious", "wink knows how you feel", "sensing the occupant's feelings"])
def test_guard_blocks_emotion_claims(text):
    with pytest.raises(EmotionClaimError):
        assert_no_emotion_claims(text)


@pytest.mark.parametrize("text", [
    "the space is predicted to read as calm", "direct sun reaches 40% of the window", "make the room calmer"])
def test_guard_allows_space_predictions(text):
    assert assert_no_emotion_claims(text) == text


def test_all_mock_text_passes_guard():
    h = MockHunchProvider()
    for ctx in [{"time_of_day": "afternoon", "sunlit_fraction": 0.5}, {"time_of_day": "night", "sunlit_fraction": 0.0}, {}]:
        obs = h.observe(ctx)
        for o in obs:
            assert_no_emotion_claims(str(o.get("label", "")) + " " + o["source"])
        assert_no_emotion_claims(h.propose_goal(obs, [RULE])["rationale"])


def test_mock_result_is_labelled():
    result = mock_result({"target": "open", "rooms": [{"name": "loft"}], "site": ""})
    assert result["mock"] is True
    assert result["provider"] == {"name": "hunch-mock", "mock": True}
    assert result["focus"]["atmosphere"]["predicted_feel"] == "open"
    assert result["focus"]["atmosphere"]["mock"] is True
    assert "site" not in result


def test_mock_worker_cli(tmp_path: Path):
    inp = tmp_path / "snap.json"
    out = tmp_path / "result.json"
    prog = tmp_path / "progress.json"
    inp.write_text(json.dumps({"target": "calm", "focus_room": "room", "rooms": [{"name": "room"}]}), encoding="utf-8")
    assert worker_main(["--input", str(inp), "--output", str(out), "--progress", str(prog)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["result"]["mock"] is True
    assert payload["result"]["focus"]["name"] == "room"
    assert json.loads(prog.read_text(encoding="utf-8"))["progress"] == 1.0
