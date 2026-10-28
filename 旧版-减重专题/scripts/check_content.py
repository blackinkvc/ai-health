#!/usr/bin/env python3
"""校验 data/nav.json 与 content/ 下的 Markdown 是否一致。"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAV = ROOT / "data" / "nav.json"


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
    nav = json.loads(NAV.read_text(encoding="utf-8"))
    errors = []
    seen_slugs = set()
    total = 0

    for category in nav["categories"]:
        for article in category["articles"]:
            total += 1
            path = ROOT / article["path"]
            if not path.exists():
                errors.append(f"缺失文件: {article['path']}")
                continue
            meta = parse_frontmatter(path.read_text(encoding="utf-8"))
            if meta.get("title") != article["title"]:
                errors.append(f"标题不一致: {article['path']} ({meta.get('title')!r} != {article['title']!r})")
            if meta.get("slug") != article["slug"]:
                errors.append(f"slug 不一致: {article['path']} ({meta.get('slug')!r} != {article['slug']!r})")
            if article["slug"] in seen_slugs:
                errors.append(f"重复 slug: {article['slug']}")
            seen_slugs.add(article["slug"])
            body = path.read_text(encoding="utf-8")
            if not re.search(r"^# .+", body, re.M):
                errors.append(f"缺少一级标题: {article['path']}")

    actual = {p.name for p in (ROOT / "content").rglob("*.md")}
    declared = {Path(a["path"]).name for c in nav["categories"] for a in c["articles"]}
    for name in sorted(actual - declared):
        errors.append(f"未登记在 nav.json: {name}")

    print(f"分类: {len(nav['categories'])}  文章: {total}  实际文件: {len(actual)}")
    if errors:
        print("\n发现问题:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("校验通过：nav.json 与 content/ 完全一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
