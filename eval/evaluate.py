"""评测：在人工标注集上算分类器的负面召回率、正常误杀率、每标签召回。

用法：
  python -m eval.evaluate        # 离线规则层评测（无需 key）
  python -m eval.evaluate --llm  # 启用 LLM 语义层评测（需 .env 配 key）
"""
import argparse
import json
from pathlib import Path

from jingtu.classifier import Classifier
from jingtu.llm import DeepSeekLLM

HERE = Path(__file__).resolve().parent


def load_dataset(path):
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [json.loads(l) for l in lines]


def evaluate(classifier, dataset):
    tp = fp = fn = 0
    per_label = {}
    for ex in dataset:
        true = set(ex["labels"])
        pred = set(classifier.classify(ex["text"])["labels"])
        if "normal" in true:
            if pred - {"normal"}:
                fp += 1
        else:
            if pred & true:
                tp += 1
            else:
                fn += 1
            for lab in true:
                hit, total = per_label.setdefault(lab, [0, 0])
                per_label[lab] = [hit + (1 if lab in pred else 0), total + 1]

    negatives = sum(1 for ex in dataset if "normal" not in ex["labels"])
    normals = sum(1 for ex in dataset if "normal" in ex["labels"])
    recall = tp / negatives if negatives else 0.0
    fpr = fp / normals if normals else 0.0

    print(f"负面召回率 recall: {recall:.1%} ({tp}/{negatives})")
    print(f"正常误杀率 false-positive: {fpr:.1%} ({fp}/{normals})")
    print("每标签召回：")
    for lab, (hit, total) in sorted(per_label.items()):
        print(f"  {lab:<20} {hit}/{total}")
    return {"recall": recall, "fpr": fpr, "per_label": per_label}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="启用 LLM 语义层")
    args = ap.parse_args()

    llm = None
    if args.llm:
        import config
        if config.DEEPSEEK_API_KEY:
            llm = DeepSeekLLM(config.DEEPSEEK_API_KEY, config.DEEPSEEK_BASE_URL, config.DEEPSEEK_MODEL)
        else:
            print("未配置 DEEPSEEK_API_KEY，回退到离线规则层。")
    dataset = load_dataset(HERE / "dataset.jsonl")
    evaluate(Classifier(llm=llm), dataset)


if __name__ == "__main__":
    main()
