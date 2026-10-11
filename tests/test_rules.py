from jingtu.rules import RuleEngine


def test_detects_abuse():
    r = RuleEngine().classify("你是个傻逼")
    assert "abuse" in r["labels"]


def test_detects_homophone_abuse():
    r = RuleEngine().classify("煞笔")
    assert "abuse" in r["labels"]


def test_detects_ascii_with_word_boundary():
    r = RuleEngine().classify("这人真是 sb")
    assert "abuse" in r["labels"]
    # 不应误伤普通英文单词里的 sb
    r2 = RuleEngine().classify("asbestos is a mineral")
    assert "abuse" not in r2["labels"]


def test_detects_passive_aggressive():
    r = RuleEngine().classify("不会吧不会吧，就这？")
    assert "passive_aggressive" in r["labels"]


def test_detects_baiting():
    r = RuleEngine().classify("又来引战，地域黑滚出去")
    assert "baiting" in r["labels"]


def test_detects_astroturf():
    r = RuleEngine().classify("不转不是中国人，让更多人看到")
    assert "astroturf" in r["labels"]


def test_normal_text():
    r = RuleEngine().classify("今天天气不错，去公园散步了")
    assert r["labels"] == []
    assert r["severity"] == 0.0
