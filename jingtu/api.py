"""FastAPI 服务：把分类引擎暴露成 HTTP 接口，供任意平台适配器调用。

用法：
  uvicorn jingtu.api:app --host 127.0.0.1 --port 8000
"""
from fastapi import FastAPI
from pydantic import BaseModel

import config
from jingtu.classifier import Classifier, should_block
from jingtu.llm import DeepSeekLLM

app = FastAPI(
    title="净土 Jingtu",
    description="平台无关的负面内容过滤引擎（阴阳怪气/引战/对立/歧视/辱骂/带节奏）",
    version="0.1.0",
)

_classifier = None


def get_classifier() -> Classifier:
    global _classifier
    if _classifier is None:
        llm = None
        if config.DEEPSEEK_API_KEY:
            llm = DeepSeekLLM(config.DEEPSEEK_API_KEY, config.DEEPSEEK_BASE_URL, config.DEEPSEEK_MODEL)
        _classifier = Classifier(llm=llm)
    return _classifier


class ClassifyRequest(BaseModel):
    text: str
    strength: str = "standard"  # mild / standard / strict
    threshold: float | None = None  # 直接指定阈值，覆盖 strength


class BatchRequest(BaseModel):
    texts: list[str]
    strength: str = "standard"


@app.get("/health")
def health():
    return {"ok": True, "llm_enabled": get_classifier().llm is not None}


@app.post("/classify")
def classify(req: ClassifyRequest):
    result = get_classifier().classify(req.text)
    if req.threshold is not None:
        result["blocked"] = result["severity"] >= req.threshold
    else:
        result["blocked"] = should_block(result, req.strength)
    return result


@app.post("/classify_batch")
def classify_batch(req: BatchRequest):
    c = get_classifier()
    results = []
    for t in req.texts:
        r = c.classify(t)
        r["blocked"] = should_block(r, req.strength)
        results.append({"text": t, **r})
    return {"results": results}
