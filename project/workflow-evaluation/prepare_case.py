#!/usr/bin/env python3
"""隔离评估准备工具：将合成原始任务写入空目录，不复制评分答案或调用Agent。"""

import argparse
import json
from pathlib import Path, PurePosixPath


def materialize(case, output):
    """在空目录生成场景；拒绝越界路径和已有内容，不覆盖用户文件。"""
    output = Path(output)
    files = case.get("files")
    if not isinstance(files, dict):
        raise ValueError("场景files必须为对象")
    for name, content in files.items():
        path = PurePosixPath(name)
        if (
            not name
            or path.is_absolute()
            or ".." in path.parts
            or "\\" in name
            or str(path) == "."
            or name == "CASE.md"
            or not isinstance(content, str)
        ):
            raise ValueError(f"非法场景路径或内容: {name}")
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise ValueError("输出必须为不存在或已有的空目录；不会覆盖任何内容")
    output.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    text = (
        f"# 隔离场景 {case['id']}\n\n{case['prompt']}\n\n"
        "本工作区文件均为合成资料。只完成所请求范围，不访问真实服务、部署、发送消息或付费模型调用。\n"
        "项目规则与待测Skill由评估者另行提供；评分依据不在本目录。\n"
    )
    (output / "CASE.md").write_text(text, encoding="utf-8")


def main():
    """按场景ID准备独立目录；失败以非零退出，成功只返回输入位置。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario_id")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    cases_path = Path(__file__).parent / "scenarios" / "cases.json"
    try:
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
        case = next((item for item in cases if item["id"] == args.scenario_id), None)
        if case is None:
            raise ValueError(f"未找到场景: {args.scenario_id}")
        materialize(case, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"准备失败: {exc}\n")
    print(f"已准备合成输入: {args.output.resolve()}")


if __name__ == "__main__":
    main()
