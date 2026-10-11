"""负面内容的分类维度定义（多标签体系）。"""

DIMENSIONS = {
    "passive_aggressive": {
        "name": "阴阳怪气/反讽",
        "severity": 0.5,
        "desc": "正话反说、反讽、冷嘲热讽、阴阳怪气",
    },
    "baiting": {
        "name": "引战/拉踩",
        "severity": 0.6,
        "desc": "故意挑事、拉踩、粉丝/地域/性别对立",
    },
    "polarization": {
        "name": "对立/扣帽子",
        "severity": 0.6,
        "desc": "站队、贴标签、地图炮、道德绑架",
    },
    "discrimination": {
        "name": "歧视/仇恨",
        "severity": 0.9,
        "desc": "种族/性别/地域/职业/外貌/疾病歧视",
    },
    "abuse": {
        "name": "辱骂/人身攻击",
        "severity": 0.9,
        "desc": "脏话、人身攻击（含谐音/首字母隐写）",
    },
    "astroturf": {
        "name": "带节奏/煽动",
        "severity": 0.6,
        "desc": "情绪煽动、阴谋论、假消息扩散",
    },
}

NORMAL = {"name": "正常", "severity": 0.0, "desc": "无负面内容"}


def severity_of(label: str) -> float:
    if label in DIMENSIONS:
        return DIMENSIONS[label]["severity"]
    return 0.0


def all_labels() -> list[str]:
    return list(DIMENSIONS.keys()) + ["normal"]
