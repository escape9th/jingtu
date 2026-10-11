from jingtu.classifier import Classifier
from jingtu.llm import FakeLLM


def test_offline_rule_only_detects_abuse():
    c = Classifier(llm=None)
    r = c.classify("你是个傻逼")
    assert r["method"] == "rule"
    assert "abuse" in r["labels"]


def test_offline_normal():
    c = Classifier(llm=None)
    r = c.classify("今天天气不错")
    assert r["labels"] == ["normal"]


def test_hybrid_llm_catches_sarcasm():
    # 规则层抓不到"阴阳怪气"，交给 LLM 语义层
    llm = FakeLLM([{"labels": ["passive_aggressive"], "severity": 0.6, "reason": "正话反说"}])
    c = Classifier(llm=llm)
    r = c.classify("哇，你可真是太聪明了呢")
    assert "passive_aggressive" in r["labels"]
    assert r["severity"] >= 0.5


def test_hybrid_rule_short_circuits_on_abuse():
    # 明显辱骂，规则层直接采信，不调 LLM（节省一次调用）
    llm = FakeLLM([])  # 空队列：若被调用会返回 normal
    c = Classifier(llm=llm)
    r = c.classify("你妈死了 nmsl")
    assert r["method"] == "rule"
    assert "abuse" in r["labels"]
    assert llm.calls == []  # 确认没有调用 LLM


def test_hybrid_merges_labels():
    llm = FakeLLM([{"labels": ["passive_aggressive", "polarization"], "severity": 0.7, "reason": "扣帽子+阴阳"}])
    c = Classifier(llm=llm)
    r = c.classify("你这种人，呵呵，差不多得了")
    assert "passive_aggressive" in r["labels"]
    assert "polarization" in r["labels"]
