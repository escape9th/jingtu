"""谐音隐写检测：把词转拼音，自动识别同音变体（如"煞笔/沙比/啥币" → "傻逼"）。

注意：只对少数"标准词"做拼音匹配，控制误报范围；纯拼音拼接偶有误伤
（如"啥比较"的拼音含"shabi"），靠 LLM 层 + 用户可点击恢复兜底。
"""
from pypinyin import lazy_pinyin

# 每个维度挑最典型的"标准词"做拼音匹配（不是全部词，避免误报面过大）
_BASE_WORDS = {
    "abuse": ["傻逼", "你妈", "草泥马", "卧槽", "他妈", "操你", "废物", "垃圾", "贱人", "脑残", "滚蛋", "去死", "杂种", "狗东西"],
    "discrimination": ["黑鬼", "支那", "智障", "娘炮", "低能", "弱智", "脑瘫"],
    "baiting": ["引战", "地域黑", "拳师", "牧羊犬", "跪舔", "洗地"],
}


def to_pinyin(text: str) -> str:
    return "".join(lazy_pinyin(text)).lower()


class HomophoneMatcher:
    def __init__(self):
        self._entries = []
        for label, words in _BASE_WORDS.items():
            for w in words:
                py = to_pinyin(w)
                if py:
                    self._entries.append((label, w, py))

    def match(self, text: str) -> tuple[set, list]:
        """返回 (命中的标签集合, 命中的标准词列表)。"""
        tp = to_pinyin(text)
        labels = set()
        matched = []
        for label, word, py in self._entries:
            if py in tp:
                labels.add(label)
                matched.append(word)
        return labels, matched
