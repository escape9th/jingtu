"""净土分类器：规则层快筛 + LLM 语义精判，融合输出多标签结果。"""
from .dimensions import severity_of
from .llm import LLM
from .rules import RuleEngine


class Classifier:
    def __init__(self, llm: LLM | None = None, rule_engine: RuleEngine | None = None):
        self.rule_engine = rule_engine or RuleEngine()
        self.llm = llm  # None 表示纯离线（只跑规则层）

    def classify(self, text: str) -> dict:
        rule = self.rule_engine.classify(text)

        # 纯离线模式：只靠规则层
        if self.llm is None:
            return {
                **rule,
                "labels": rule["labels"] or ["normal"],
                "reason": "、".join(rule["matched"]) if rule["matched"] else "",
                "method": "rule",
                "confidence": 1.0 if rule["labels"] else 0.6,
            }

        # 明显负面（辱骂/歧视，severity 0.9）→ 规则层直接采信，省一次 LLM 调用
        if rule["severity"] >= 0.9:
            return {
                **rule,
                "reason": "、".join(rule["matched"]),
                "method": "rule",
                "confidence": 0.95,
            }

        # 语义层补漏（能懂阴阳怪气、反讽、谐音）
        llm_result = self.llm.classify(text)
        if not llm_result:
            return {
                **rule,
                "labels": rule["labels"] or ["normal"],
                "method": "rule",
                "confidence": 0.6,
            }
        return self._merge(rule, llm_result)

    def _merge(self, rule: dict, llm_result: dict) -> dict:
        llm_labels = set(llm_result.get("labels", []))
        rule_labels = set(rule["labels"])
        # 规则命中优先；LLM 的 normal 不覆盖规则命中
        labels = rule_labels | (llm_labels - {"normal"})
        severity = max(rule["severity"], llm_result.get("severity", 0.0))
        reason = llm_result.get("reason", "")
        if rule["matched"] and reason:
            reason += f"（规则命中：{', '.join(rule['matched'])}）"
        return {
            "labels": sorted(labels) or ["normal"],
            "severity": severity,
            "reason": reason,
            "matched": rule["matched"],
            "method": "hybrid" if labels else "llm",
            "confidence": llm_result.get("confidence", 0.8),
        }
