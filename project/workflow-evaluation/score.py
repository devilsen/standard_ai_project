#!/usr/bin/env python3
"""工作流评估工具：校验人工评分并计算加权结果，不判断任务语义正确性。"""

import argparse
import json
from pathlib import Path


WEIGHTS = {
    "requirements": 20,
    "scope": 15,
    "consistency": 15,
    "decisions": 15,
    "implementation": 15,
    "evidence": 20,
}


def nonempty_text(value):
    """判断来源/原因字段是否有文本；文本内容仍需评审者核验。"""
    return isinstance(value, str) and bool(value.strip())


def evaluate(card):
    """校验评分形态并计算适用维度；缺评分返回incomplete，致命问题不能被均分覆盖。"""
    if not isinstance(card, dict):
        raise ValueError("scorecard必须为对象")
    for field in ("scenario_id", "run_id", "skill_revision", "conditions", "reviewer"):
        if not nonempty_text(card.get(field)):
            raise ValueError(f"缺少有效字段: {field}")
    ratings = card.get("ratings")
    if not isinstance(ratings, dict) or set(ratings) - set(WEIGHTS):
        raise ValueError("ratings必须为已知维度的对象")
    fatal = card.get("fatal_issues")
    if not isinstance(fatal, list):
        raise ValueError("fatal_issues必须为数组")
    for issue in fatal:
        if not isinstance(issue, dict) or not all(
            nonempty_text(issue.get(key)) for key in ("issue", "evidence")
        ):
            raise ValueError("每项致命问题需要issue与evidence")

    missing = []
    weighted = 0
    applicable_weight = 0
    scores = []
    for key, weight in WEIGHTS.items():
        item = ratings.get(key)
        if item is None:
            missing.append(key)
            continue
        if not isinstance(item, dict) or type(item.get("applicable")) is not bool:
            raise ValueError(f"{key}: applicable必须为布尔值")
        if not item["applicable"]:
            if not nonempty_text(item.get("reason")):
                raise ValueError(f"{key}: 不适用必须说明reason")
            if item.get("score") is not None:
                raise ValueError(f"{key}: 不适用项不能同时评分")
            continue
        score = item.get("score")
        refs = item.get("evidence")
        if score is None or not isinstance(refs, list) or not refs:
            missing.append(key)
            continue
        if type(score) is not int or not 0 <= score <= 4:
            raise ValueError(f"{key}: score必须为0到4的整数")
        if not all(nonempty_text(ref) for ref in refs):
            raise ValueError(f"{key}: evidence引用不能为空")
        weighted += weight * score / 4
        applicable_weight += weight
        scores.append(score)

    if not applicable_weight:
        missing.append("no_applicable_scored_dimensions")
    total = round(weighted / applicable_weight * 100, 2) if applicable_weight else None
    if fatal:
        status = "fatal"
    elif missing:
        status = "incomplete"
    elif total >= 85 and min(scores) >= 3:
        status = "candidate"
    else:
        status = "needs_improvement"
    return {
        "scenario_id": card["scenario_id"],
        "run_id": card["run_id"],
        "status": status,
        "score": total if not missing else None,
        "applicable_weight": applicable_weight,
        "missing": missing,
        "fatal_issues": fatal,
        "note": "仅计算人工评分；candidate不是业务发布批准，也不证明评分证据真实",
    }


def main():
    """从JSON评分表读取输入，输出计算结果；无效输入以非零退出。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scorecard", type=Path)
    args = parser.parse_args()
    try:
        card = json.loads(args.scorecard.read_text(encoding="utf-8"))
        result = evaluate(card)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"评分输入无效: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
