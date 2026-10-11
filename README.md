# 净土 Jingtu 🕊️ 平台无关的负面内容过滤引擎 / Platform-Agnostic Toxic Content Filter

> 让「阴阳怪气、引战、对立、歧视、辱骂、带节奏」无处遁形。给任意平台装上净化滤镜，还你一片能安心刷的净土。
> *Detect passive-aggression, baiting, polarization, discrimination, abuse, and astroturfing — pluggable into any platform.*

## 🌱 愿景 Vision

刷社交媒体时，我们不想被算法喂「引战、对立、歧视、阴阳怪气」，却很难靠平台的「不感兴趣」精准排除。净土的目标是做一个**平台无关的负面内容过滤引擎**：任何平台接入它，就能把这类内容提前折叠/屏蔽——**过滤的是"让人看了上火"的内容，而不是"我不认同的观点"**。

*When scrolling, we don't want the algorithm feeding us baiting, polarization, discrimination, or passive-aggression — yet "Not interested" rarely excludes them precisely. Jingtu is a platform-agnostic filter engine: any platform can plug it in to fold/hide such content — filtering "rage-inducing content", not "opinions I disagree with".*

> ⚠️ 当前是 v0.1 地基：核心分类引擎 + 第一个适配器（浏览器插件）+ 评测。离"改变世界"还差很多，但最硬的地基已经打好了。

## 🔑 Keywords / 关键词

`Content Moderation` · `Toxic Comment Classification` · `AI Agent` · `LLM` · `DeepSeek` · `Sarcasm Detection` · `Passive-Aggression` · `Hate Speech` · `阴阳怪气` · `反讽` · `引战` · `对立` · `歧视` · `辱骂` · `带节奏` · `谐音隐写` · `浏览器插件` · `FastAPI` · `Python`

## 🧭 它能识别什么 / What it detects（多标签）

| 标签 Label | 含义 | severity |
|-----------|------|----------|
| `abuse` | 辱骂/人身攻击（含谐音、首字母隐写） | 0.9 |
| `discrimination` | 歧视/仇恨（种族/性别/地域/职业/外貌） | 0.9 |
| `baiting` | 引战/拉踩/饭圈/地域黑 | 0.6 |
| `polarization` | 对立/扣帽子/地图炮/道德绑架 | 0.6 |
| `astroturf` | 带节奏/煽动/阴谋论 | 0.6 |
| `passive_aggressive` | 阴阳怪气/反讽 | 0.5 |
| `normal` | 正常 | 0.0 |

每条文本输出：多标签 + `severity`（严重度）+ `reason`（理由）+ `blocked`（是否该屏蔽）。

## 🏗 架构 Architecture

```
【核心引擎 jingtu/】—— 平台无关，纯文本进出
  规则层 rules.py     离线、零成本：词典 + 阴阳怪气句式 + 谐音/首字母隐写
        ↓（规则层拿不准/纯离线）
  LLM 语义层 llm.py   语境判断：能懂反讽、阴阳怪气（DeepSeek，可选）

【适配器 adapters】—— 把引擎装到平台
  API    jingtu/api.py        FastAPI：POST /classify
  浏览器插件 extension/       监听 DOM → 调本地服务 → 折叠负面内容
  未来   Android 无障碍 / iOS / 更多平台
```

**核心设计**：规则层求「高精度」（宁可漏、不误杀），LLM 层补「召回」（懂语境）。明显辱骂/歧视直接规则层采信，省 LLM 调用。

## 🚀 快速开始 Quick Start

```bash
# 1. 装依赖
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 命令行（纯离线，无需任何 key）
python -m jingtu.cli "你是个傻逼"
python -m jingtu.cli "不会吧不会吧，就这？"
# 启用 LLM 语义层（先复制 .env.example 为 .env 填 DEEPSEEK_API_KEY）
python -m jingtu.cli "哇，你可真是太聪明了呢" --llm

# 3. 启动 HTTP 服务（供浏览器插件等调用）
uvicorn jingtu.api:app --host 127.0.0.1 --port 8000
#   然后到 Chrome 加载 extension/ 目录，即可在网页上自动折叠负面评论

# 4. 跑测试 / 评测
python -m pytest -q
python -m eval.evaluate
```

## 📊 评测结果 Evaluation（离线规则层，22 条人工标注）

| 指标 | 结果 |
|------|------|
| 负面召回 recall | **80.0%**（12/15） |
| 正常误杀 false-positive | **0.0%**（0/7） |

> 注：这是**规则层离线基线**（小标注集，仅作参考）。语义型内容（阴阳怪气、反讽）规则层天然够不到，由 LLM 层补召回。

## 📁 目录 Structure

```
jingtu/
  jingtu/            # 核心引擎（rules/llm/classifier/dimensions/api/cli）
  extension/         # 浏览器插件适配器（Manifest V3）
  eval/              # 评测集 + 评测脚本
  tests/             # 15 个单元测试
  docs/RESEARCH.md   # 研究笔记（现状盘点 + 设计依据）
```

## 🗺 路线图 Roadmap

- [ ] LLM 语义层评测（接入真实 key 后的全引擎指标）
- [ ] 谐音/形近/拼音变体自动扩展（pypinyin + 形近字表）
- [ ] 更多平台适配器（Android 无障碍、X/B站/抖音 selector 精调）
- [ ] 用户自定义过滤强度（温和/标准/严格）+ 白名单
- [ ] 更大的人工标注评测集 + 微调小模型降成本

## ⚖️ 免责声明 Disclaimer

本项目仅用于个人内容过滤。自动化修改平台页面/App 行为可能违反某些平台服务条款，请自行评估使用场景与风险。
