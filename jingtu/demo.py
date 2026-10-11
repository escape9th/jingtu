"""演示：对一批示例文本跑分类，打印结果表（纯离线，无需 key）。

用法：python -m jingtu.demo
"""
from .classifier import Classifier

EXAMPLES = [
    "你是个傻逼",
    "煞笔一个",
    "你就是个啥币",          # 谐音隐写 → 傻逼
    "不会吧不会吧，就这？",
    "哇，你可真是太聪明了呢",  # 反讽（规则层够不到，LLM 能懂）
    "男拳师别来沾边",
    "黑鬼就是低等种族",
    "不转不是中国人",
    "这人就是个键盘侠",
    "这首经典音乐真好听",      # 不应误杀
    "孝顺父母是传统美德",      # 不应误杀
    "今天天气不错，去公园散步",
]


def main() -> int:
    c = Classifier()  # 离线规则层
    print(f"{'判定':<2} {'severity':<9} {'标签':<24} 文本")
    print("-" * 70)
    for t in EXAMPLES:
        r = c.classify(t)
        labels = ", ".join(r["labels"]) or "normal"
        mark = "[屏蔽]" if r["severity"] >= 0.5 else "[正常]"
        print(f"{mark} {r['severity']:<4.1f} {labels:<24} {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
