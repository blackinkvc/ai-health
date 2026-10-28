#!/usr/bin/env python3
"""校验营养学资料库的目录、模块导读与 data/nav.json 是否一致。"""

import json
import re
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent
NAV = LIB / "data" / "nav.json"

STATUS_VALUES = {"planned", "draft", "review", "published"}
errors = []
warnings = []


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = {}
    for line in text[3:end].strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def main() -> int:
    if not NAV.exists():
        print(f"缺少导航文件: {NAV}")
        return 1

    nav = json.loads(NAV.read_text(encoding="utf-8"))
    modules = nav.get("modules", [])
    slugs = set()
    total_topics = 0
    status_count = {key: 0 for key in STATUS_VALUES}

    for module in modules:
        module_dir = LIB / module["dir"]
        if not module_dir.is_dir():
            errors.append(f"缺少模块目录: {module['dir']}")
            continue

        guide = LIB / module["guide"]
        if not guide.exists():
            errors.append(f"缺少模块导读: {module['guide']}")
        else:
            meta = parse_frontmatter(guide.read_text(encoding="utf-8"))
            if meta.get("slug") != f"guide-{module['id']}":
                warnings.append(f"导读 slug 不匹配: {module['guide']}")

        for topic in module["topics"]:
            total_topics += 1
            if topic["slug"] in slugs:
                errors.append(f"重复 slug: {topic['slug']}")
            slugs.add(topic["slug"])

            status = topic.get("status", "planned")
            if status not in STATUS_VALUES:
                errors.append(f"非法状态 {status}: {topic['slug']}")
            else:
                status_count[status] += 1

            planned = LIB / topic["plannedPath"]
            if not planned.parent.is_dir():
                errors.append(f"主题路径的目录不存在: {topic['plannedPath']}")
            if status != "planned" and not planned.exists():
                errors.append(f"状态为 {status} 但文件不存在: {topic['plannedPath']}")

    # 找出未登记在 nav.json 的文章
    declared = {item["plannedPath"] for m in modules for item in m["topics"]}
    for path in LIB.glob("*/*.md"):
        if path.name in {"00-模块导读.md"} or path.parent.name in {"00-总览", "_模板"}:
            continue
        relative = f"{path.parent.name}/{path.name}"
        if relative not in declared:
            warnings.append(f"未登记的文章: {relative}")

    print(f"模块: {len(modules)}  主题: {total_topics}  已发布: {status_count['published']}  "
          f"审校: {status_count['review']}  草稿: {status_count['draft']}  待补充: {status_count['planned']}")

    if warnings:
        print("\n提示:")
        for item in warnings:
            print(f"  - {item}")
    if errors:
        print("\n错误:")
        for item in errors:
            print(f"  - {item}")
        return 1

    print("校验通过：目录、导读与 nav.json 一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
