# 净土 Jingtu · 研究笔记

## 一、现状盘点（有没有人做过）

| 方向 | 代表工作 | 与「阴阳怪气/引战」的关系 |
|------|---------|------------------------|
| 反讽/讽刺检测 | [CFMS 多模态反讽基准](https://arxiv.org/pdf/2604.16372v1)、[FGVIrony 细粒度反语](https://www.sciencedirect.com/science/article/abs/pii/S0306457325001104)、[大规模中文反讽数据集](https://www.sciopen.com/local/article_pdf/10.26599/TST.2025.9010146.pdf) | 最接近，但只管「修辞反转」，不含引战/对立 |
| 辱骂/冒犯检测 | [offensive_detect](https://github.com/guo-lin-jie/offensive_detect)、[谐音隐写检测](https://aclanthology.cn/2025.emnlp-industry.172/)（EMNLP 2025） | 管直白骂人 + 谐音，不管阴阳怪气 |
| 现成过滤工具 | [DetoxAI](https://chromewebstore.google.com/detail/detoxai-filter-for-x-redd/mcghgpgjdabokdlpglobpldfplpeoigc)、[TakeBack](https://chromewebstore.google.com/detail/takeback-content-filter-w/paiidckpbpkkjhicmbgmohnmjcdbchef)、[评论净化器](https://chromewebstore.google.com/detail/comment-purifier-block-to/dnkfkdjbbdknmaaonbnobmahiejfhefb)、[filter-youtube-comments](https://github.com/get543/filter-youtube-comments) | 浏览器插件、关键词为主、主要西方平台 |

**结论**：`阴阳怪气 + 引战 + 对立 + 扣帽子 + 带节奏` 作为一个统一概念，**没有公开数据集、没有专门模型**。这是空白 = 机会。

## 二、技术设计

1. **双层分类**：
   - **规则层**（离线、零成本）：词典 + 句式匹配，覆盖谐音/首字母隐写（参考专利 [CN113486656A 变种词表](http://patentimages.storage.googleapis.com/39/b3/d6/8e173be8370aa4/CN113486656A.pdf)：形近词/拼音词/音近词）、阴阳怪气惯用句式。
   - **LLM 语义层**（需 key）：能懂语境、反讽、阴阳怪气——这是规则层永远补不上的部分。
2. **多标签体系**：passive_aggressive / baiting / polarization / discrimination / abuse / astroturf / normal，每条文本可多标签 + severity + reason。
3. **平台无关架构**：核心引擎（纯文本进出）→ 适配器（浏览器插件 / HTTP API / 未来移动端）。

## 三、关键挑战

- **误杀 vs 漏判**：规则层求「高精度」（宁可漏，不误杀），LLM 层补「召回」。歧义词（如"笑死我了"）必须交给 LLM 判断语境。
- **主观性**：引战/对立有语境，同一句话在不同帖子里含义不同。
- **隐写形态**：谐音、首字母、emoji、形近字，规则层只能穷举，LLM 层靠语义。
- **实时性**：评论流实时刷，每条过 LLM 有成本；规则层先粗筛、LLM 精判是正解。

## 四、参考链接

- 谐音隐写冒犯检测（EMNLP 2025）：https://aclanthology.cn/2025.emnlp-industry.172/
- 变种词表专利（形近/拼音/音近）：http://patentimages.storage.googleapis.com/39/b3/d6/8e173be8370aa4/CN113486656A.pdf
- 个性化有害内容检测（ICL）：https://huggingface.co/papers/2511.05532
- LLM 微调仇恨言论检测：https://link.springer.com/article/10.1007/s44163-026-02354-1
