from jingtu.llm import extract_json


def test_extract_json_object():
    assert extract_json('{"labels": ["abuse"], "severity": 0.9}') == {"labels": ["abuse"], "severity": 0.9}


def test_extract_with_fence():
    assert extract_json('```json\n{"labels": ["normal"], "severity": 0}\n```') == {"labels": ["normal"], "severity": 0}


def test_extract_none():
    assert extract_json("没有 json") is None
