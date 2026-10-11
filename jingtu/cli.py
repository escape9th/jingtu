"""命令行工具：读入文本，输出分类结果。

用法：
  python -m jingtu.cli "你是个傻逼"
  echo "不会吧不会吧" | python -m jingtu.cli
  python -m jingtu.cli "文本" --llm --json   # 启用 LLM 语义层
"""
import argparse
import json
import sys

from .classifier import Classifier
from .llm import DeepSeekLLM


def build_classifier(use_llm: bool, api_key: str, base_url: str, model: str) -> Classifier:
    llm = None
    if use_llm and api_key:
        llm = DeepSeekLLM(api_key, base_url, model)
    return Classifier(llm=llm)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="净土：负面内容分类器")
    ap.add_argument("text", nargs="?", help="要分类的文本")
    ap.add_argument("--llm", action="store_true", help="启用 LLM 语义层（需 .env 配 key）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    import config  # 延迟导入，避免未装 dotenv 时报错
    c = build_classifier(args.llm, config.DEEPSEEK_API_KEY, config.DEEPSEEK_BASE_URL, config.DEEPSEEK_MODEL)

    if args.text:
        texts = [args.text]
    elif not sys.stdin.isatty():
        texts = [line.strip() for line in sys.stdin if line.strip()]
    else:
        ap.print_help()
        return 1

    for t in texts:
        r = c.classify(t)
        if args.json:
            print(json.dumps({"text": t, **r}, ensure_ascii=False))
        else:
            labels = ", ".join(r["labels"]) or "-"
            print(f"[{r['severity']:.1f}] {labels:<28} | {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
