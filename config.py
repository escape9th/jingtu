"""全局配置：从 .env 读取，未设置时用默认值。"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent

# LLM 语义层（可选）：填了 key 才启用，否则纯离线规则层
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 屏蔽阈值：severity >= 此值就判定为需要屏蔽
BLOCK_THRESHOLD = float(os.getenv("BLOCK_THRESHOLD", "0.5"))
