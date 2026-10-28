#!/usr/bin/env python3
"""对 68 篇文章做自动化审校，输出 data/qa-report.json 和 data/qa-report.md。"""

import json
import re
from collections import Counter
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent
NAV = LIB / "data" / "nav.json"


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, text[end + 4:]


def audit_article(module, topic, path):
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    flags = []

    required = ["title", "slug", "module", "order", "status", "tags", "summary", "updated"]
    for key in required:
        if key not in meta:
            flags.append(f"缺少元数据 {key}")

    if meta.get("title") != topic["title"]:
        flags.append("标题与 nav.json 不一致")
    if meta.get("slug") != topic["slug"]:
        flags.append("slug 与 nav.json 不一致")
    if meta.get("module") != module["title"]:
        flags.append("模块名与 nav.json 不一致")
    if meta.get("status") not in {"planned", "draft", "review", "published"}:
        flags.append(f"非法状态 {meta.get('status')}")

    headings = re.findall(r"^(#{1,6})\s+(.+)$", body, flags=re.M)
    h1 = [h for h in headings if len(h[0]) == 1]
    if len(h1) != 1:
        flags.append(f"一级标题数量为 {len(h1)}")
    elif h1[0][1].strip() != topic["title"]:
        flags.append("正文一级标题与标题不一致")

    levels = [len(h[0]) for h in headings]
    for prev, cur in zip(levels, levels[1:]):
        if cur > prev + 1:
            flags.append(f"标题层级跳跃：H{prev} → H{cur}")
            break

    if "## 参考来源" not in body:
        flags.append("缺少参考来源")
    if "## 常见误区" not in body:
        flags.append("缺少常见误区")
    if "## 实操建议" not in body:
        flags.append("缺少实操建议")

    placeholders = [x for x in ["待补充", "TODO", "TBD", "lorem", "占位"] if x in body]
    if placeholders:
        flags.append("包含占位词：" + "、".join(placeholders))

    md_links = re.findall(r"\]\(([^)]+\.md)(?:#[^)]*)?\)", body)
    broken = []
    for target in md_links:
        if target.startswith(("http://", "https://")):
            continue
        if not (path.parent / target).resolve().exists():
            broken.append(target)
    if broken:
        flags.append("失效的 md 链接：" + "、".join(broken[:3]))

    if len(meta.get("summary", "")) < 15:
        flags.append("摘要过短")

    tags = meta.get("tags", "")
    if not tags.startswith("[") or len(tags) < 6:
        flags.append("标签格式或数量异常")

    table_rows = len(re.findall(r"^\|", body, flags=re.M))
    return {
        "module": module["title"],
        "module_id": module["id"],
        "order": topic["order"],
        "title": topic["title"],
        "slug": topic["slug"],
        "status": meta.get("status"),
        "chars": len(body),
        "h2": sum(1 for h in headings if len(h[0]) == 2),
        "tables": table_rows,
        "links": len(md_links),
        "flags": flags,
    }


def main():
    nav = json.loads(NAV.read_text(encoding="utf-8"))
    records = []
    for module in nav["modules"]:
        for topic in module["topics"]:
            path = LIB / topic["plannedPath"]
            if not path.exists():
                records.append(
                    {
                        "module": module["title"],
                        "module_id": module["id"],
                        "order": topic["order"],
                        "title": topic["title"],
                        "slug": topic["slug"],
                        "status": topic.get("status"),
                        "chars": 0,
                        "h2": 0,
                        "tables": 0,
                        "links": 0,
                        "flags": ["文件不存在"],
                    }
                )
                continue
            records.append(audit_article(module, topic, path))

    total = len(records)
    flagged = [r for r in records if r["flags"]]
    chars = sum(r["chars"] for r in records)
    status_count = Counter(r["status"] for r in records)
    flag_count = Counter(flag.split("：")[0] for r in flagged for flag in r["flags"])

    report = {
        "generated": "2026-10-25",
        "total": total,
        "total_chars": chars,
        "average_chars": round(chars / total) if total else 0,
        "status": dict(status_count),
        "flagged_articles": len(flagged),
        "flag_counts": dict(flag_count),
        "articles": records,
    }
    (LIB / "data" / "qa-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# 内容审校报告",
        "",
        f"- 生成日期：2026-10-25",
        f"- 文章总数：{total}",
        f"- 总字符：{chars:,}",
        f"- 平均字符：{report['average_chars']:,}",
        f"- 状态分布：{', '.join(f'{k} {v}' for k, v in status_count.items())}",
        f"- 有问题文章：{len(flagged)}",
        "",
        "## 问题汇总",
        "",
    ]
    if flag_count:
        lines += ["| 问题 | 篇数 |", "|---|---|"]
        for flag, count in flag_count.most_common():
            lines.append(f"| {flag} | {count} |")
    else:
        lines.append("未发现自动化可识别的问题。")

    lines += ["", "## 分模块统计", "", "| 模块 | 篇数 | 字符数 | 平均字符 | 问题数 |", "|---|---|---|---|---|"]
    for module in nav["modules"]:
        items = [r for r in records if r["module_id"] == module["id"]]
        module_chars = sum(r["chars"] for r in items)
        lines.append(
            f"| {module['title']} | {len(items)} | {module_chars:,} | "
            f"{round(module_chars / len(items)) if items else 0:,} | {sum(1 for r in items if r['flags'])} |"
        )

    lines += ["", "## 需要处理的文章", ""]
    if flagged:
        for record in flagged:
            lines.append(f"### {record['title']}（{record['module']}）")
            lines.append("")
            for flag in record["flags"]:
                lines.append(f"- {flag}")
            lines.append("")
    else:
        lines.append("无。")

    (LIB / "data" / "qa-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"审校完成：{total} 篇，{len(flagged)} 篇有待处理标记，总字符 {chars:,}")
    if flag_count:
        for flag, count in flag_count.most_common():
            print(f"  - {flag}: {count}")


if __name__ == "__main__":
    main()
