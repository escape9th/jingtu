from jingtu.classifier import STRENGTH, should_block


def test_strength_thresholds():
    assert STRENGTH["mild"] > STRENGTH["standard"] > STRENGTH["strict"]


def test_should_block_mild_only_blocks_severe():
    # 阴阳怪气 severity 0.5：mild 不拦，standard 拦
    assert should_block({"severity": 0.5}, "mild") is False
    assert should_block({"severity": 0.5}, "standard") is True


def test_should_block_abuse_everywhere():
    # 辱骂 severity 0.9：三档都拦
    assert should_block({"severity": 0.9}, "mild") is True
    assert should_block({"severity": 0.9}, "standard") is True
    assert should_block({"severity": 0.9}, "strict") is True


def test_should_block_normal_never():
    assert should_block({"severity": 0.0}, "strict") is False
