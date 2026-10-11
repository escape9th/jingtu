"""防误杀回归测试：单字词、常见正常词不应被判为负面。"""
from jingtu.rules import RuleEngine


def test_classic_music_not_flagged():
    r = RuleEngine().classify("这首经典音乐真好听")
    assert "passive_aggressive" not in r["labels"]


def test_dictionary_not_flagged():
    r = RuleEngine().classify("这本字典很好用")
    assert r["labels"] == []


def test_filial_piety_not_flagged():
    r = RuleEngine().classify("孝顺父母是传统美德")
    assert r["labels"] == []


def test_hiking_not_flagged():
    r = RuleEngine().classify("周末去爬山放松一下")
    assert r["labels"] == []


def test_scroll_not_flagged():
    r = RuleEngine().classify("页面滚动条卡住了")
    assert r["labels"] == []


def test_yinyangshi_not_flagged():
    r = RuleEngine().classify("我在玩阴阳师这个游戏")
    assert r["labels"] == []
