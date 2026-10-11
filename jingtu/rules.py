"""规则层：用词典 + 句式匹配 + 谐音隐写，离线、零成本地识别明显负面内容。

设计要点：
- 中文词用子串匹配；ASCII 词（sb/nt/tmd 等）用词边界匹配，避免误伤英文单词。
- 词典覆盖谐音 / 首字母 / 阴阳怪气惯用句式等常见隐写形态。
- 规则层追求「高精度」，宁可漏判也不误杀；语义层（LLM）负责补漏。
"""
import re

from .dimensions import severity_of
from .homophone import HomophoneMatcher

PASSIVE_AGGRESSIVE = [
    "就这", "就这就这", "不会吧", "不会吧不会吧", "急了", "急眼", "破防", "破防了",
    "典", "典中典", "乐", "绷", "绷不住", "蚌埠住了", "孝", "孝死", "孝子", "赢", "赢麻了",
    "啊对对对", "你开心就好", "你说得对", "你说是那就是", "太典了", "太对辣",
    "急了急了", "不会真有人", "真有人觉得", "差不多得了", "别洗了", "洗洗睡吧",
    "破大防", "不会吧阿sir", "你说是就是吧",
    "阴阳", "阴阳怪气", "正话反说", "好一个", "真是太好笑了", "有被笑到",
    "你可真行", "厉害死了", "真是服了", "典急孝乐赢",
]
BAITING = [
    "引战", "拉踩", "踩一捧一", "别来沾边", "滚出去", "滚出", "不欢迎",
    "脑残粉", "饭圈", "毒唯", "对家", "抬杠", "杠精", "地域黑", "地图炮",
    "男拳", "女拳", "拳师", "打拳", "田园女权", "普信男", "普信女",
    "慕洋", "牧羊犬", "跪舔", "洗地", "五毛", "美分", "精日", "精韩",
    "双标", "带节奏", "扣帽子", "道德绑架", "性别对立", "制造对立",
    "别来", "滚", "爬", "不配", "对线", "开团",
]
POLARIZATION = [
    "圣母", "圣母婊", "白莲花", "理中客", "公知", "小粉红", "键盘侠", "喷子", "红卫兵",
    "站队", "非黑即白", "二极管", "脑回路", "扣帽子", "贴标签", "地图炮", "道德绑架",
    "理客中", "牧羊", "五毛党", "美分党", "洗脑怪",
]
DISCRIMINATION = [
    "黄祸", "支那", "黑鬼", "白皮猪", "眯眯眼", "ching chong",
    "娘炮", "男人婆", "女司机", "剩女", "扶弟魔",
    "外地人", "乡巴佬", "土包子", "硬盘", "井盖",
    "汉奸", "卖国贼", "绿茶",
    "侏儒", "残废", "智障", "脑瘫", "弱智", "疯子", "神经病",
    "低等", "劣等", "人种", "种族",
]
ABUSE = [
    "傻逼", "sb", "煞笔", "沙比", "傻比", "尼玛", "你妈", "nmsl", "你妈死了",
    "草泥马", "卧槽", "我操", "cnm", "tmd", "他妈", "特么", "操你", "日你",
    "滚蛋", "去死", "废物", "垃圾", "辣鸡", "lj", "狗东西", "狗比", "狗日的",
    "畜生", "贱人", "婊子", "贱货", "烂货", "骚货", "你爹", "你大爷",
    "孤儿", "没妈", "脑残", "nt", "低能", "傻狗", "杂种", "畜生不如",
]
ASTROTURF = [
    "不转不是中国人", "转发扩散", "曝光", "顶我上去", "让更多人看到", "删前速看",
    "细思极恐", "懂的都懂", "你品你细品", "内幕", "黑幕", "阴谋",
    "割韭菜", "恰烂钱", "洗脑", "颠倒黑白", "一手遮天",
    "阴谋论", "假新闻", "造谣", "据说", "内部消息",
]

ASCII_TERMS = {"sb", "nt", "tmd", "cnm", "lj", "nmsl", "nm"}

_RULE_SETS = [
    ("passive_aggressive", PASSIVE_AGGRESSIVE),
    ("baiting", BAITING),
    ("polarization", POLARIZATION),
    ("discrimination", DISCRIMINATION),
    ("abuse", ABUSE),
    ("astroturf", ASTROTURF),
]


class RuleEngine:
    def __init__(self):
        self._patterns = []
        for label, terms in _RULE_SETS:
            for t in terms:
                self._patterns.append((label, t.lower()))
        self._homophone = HomophoneMatcher()

    def classify(self, text: str) -> dict:
        lower = (text or "").lower()
        labels = set()
        matched = []
        for label, term in self._patterns:
            if term in ASCII_TERMS:
                if re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])", lower):
                    labels.add(label)
                    matched.append(term)
            else:
                if term in lower:
                    labels.add(label)
                    matched.append(term)
        # 谐音隐写（拼音同音自动识别）
        h_labels, h_words = self._homophone.match(text)
        labels |= h_labels
        matched += [f"谐音:{w}" for w in h_words]
        severity = max((severity_of(l) for l in labels), default=0.0)
        return {
            "labels": sorted(labels),
            "matched": sorted(set(matched)),
            "severity": severity,
        }
