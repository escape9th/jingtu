from jingtu.homophone import HomophoneMatcher


def test_detects_homophone_abuse():
    m = HomophoneMatcher()
    labels, words = m.match("煞笔")
    assert "abuse" in labels
    assert "傻逼" in words


def test_detects_pinyin_euphemism():
    # "啥币" 是 "傻逼" 的同音隐写
    m = HomophoneMatcher()
    labels, _ = m.match("你就是个啥币")
    assert "abuse" in labels


def test_does_not_false_positive():
    m = HomophoneMatcher()
    labels, _ = m.match("今天天气不错")
    assert labels == set()
