"""LLM 语义层：对规则层拿不准的文本做语境判断（能懂阴阳怪气、反讽）。"""
import json

import requests


def extract_json(text: str):
    """从 LLM 输出里抠出第一个 JSON 数组/对象（容忍 ```json 围栏和废话）。"""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        first_nl = text.find("\n")
        text = text[first_nl + 1:] if first_nl != -1 else text
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    for i, ch in enumerate(text):
        if ch in "[{":
            for end in range(len(text), i, -1):
                candidate = text[i:end]
                try:
                    return json.loads(candidate)
                except (json.JSONDecodeError, ValueError):
                    continue
            break
    return None


class LLM:
    def classify(self, text: str) -> dict:
        raise NotImplementedError


class DeepSeekLLM(LLM):
    SYSTEM = (
        "你是「净土」内容过滤器。判断一条中文社交媒体文本是否属于负面内容，并分类。\n"
        "可选标签：passive_aggressive(阴阳怪气/反讽)、baiting(引战/拉踩)、"
        "polarization(对立/扣帽子)、discrimination(歧视/仇恨)、abuse(辱骂)、"
        "astroturf(带节奏/煽动)、normal(正常)。\n"
        "只输出一个 JSON 对象：{\"labels\": [\"...\"], \"severity\": 0到1的浮点数, \"reason\": \"一句话理由\"}。\n"
        "正常文本 labels 为 [\"normal\"]、severity 为 0；负面可多标签并列。不要输出 JSON 以外的内容。\n"
        "示例：\n"
        "- \"哇，你可真是太聪明了呢\" → {\"labels\": [\"passive_aggressive\"], \"severity\": 0.5, \"reason\": \"正话反说，反讽\"}\n"
        "- \"XX人都是小偷\" → {\"labels\": [\"discrimination\"], \"severity\": 0.9, \"reason\": \"群体歧视/地图炮\"}\n"
        "- \"这个观点我不太同意，理由是……\" → {\"labels\": [\"normal\"], \"severity\": 0, \"reason\": \"正常表达不同意见\"}\n"
        "- \"今天天气不错\" → {\"labels\": [\"normal\"], \"severity\": 0, \"reason\": \"\"}"
    )

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _chat(self, messages, temperature=0.0) -> str:
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "messages": messages, "temperature": temperature},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def classify(self, text: str) -> dict:
        messages = [
            {"role": "system", "content": self.SYSTEM},
            {"role": "user", "content": text},
        ]
        raw = self._chat(messages)
        data = extract_json(raw)
        if not isinstance(data, dict):
            return {}
        labels = data.get("labels", [])
        if not isinstance(labels, list):
            labels = [str(labels)]
        try:
            severity = float(data.get("severity", 0.0) or 0.0)
        except (TypeError, ValueError):
            severity = 0.0
        return {
            "labels": [str(l) for l in labels],
            "severity": max(0.0, min(1.0, severity)),
            "reason": str(data.get("reason", "")),
            "confidence": 0.85,
        }


class FakeLLM(LLM):
    """测试用：按调用顺序返回预设分类结果。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def classify(self, text: str) -> dict:
        self.calls.append(text)
        return self.responses.pop(0) if self.responses else {"labels": ["normal"], "severity": 0.0, "reason": ""}
