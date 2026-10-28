#!/usr/bin/env python3
"""把营养学资料库的 Markdown 构建成静态 HTML 站点。

依赖：pandoc（已在系统中安装）。
输出：pages/index.html、pages/module/*.html、pages/topic/*.html、
      pages/master-index.html、pages/learning-paths.html、pages/glossary.html
"""

import html
import json
import os
import re
import subprocess
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent
PAGES = LIB / "pages"
ASSETS = PAGES / "assets"
SITE_TITLE = "营养学资料库"
SITE_SUBTITLE = "系统化、可扩展、循证的营养知识体系"
STATUS_LABEL = {"planned": "待补充", "draft": "初稿", "review": "审校中", "published": "已发布"}

MODULE_ICONS = {}


def frontmatter(text: str) -> tuple[dict, str]:
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


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"[*_>#|]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def pandoc_convert(body: str) -> tuple[str, str]:
    result = subprocess.run(
        [
            "pandoc",
            "-f",
            "markdown",
            "-t",
            "html5",
            "--toc",
            "--toc-depth=2",
            "--wrap=none",
            "--no-highlight",
            "-s",
            "--metadata",
            "title=doc",
        ],
        input=body,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    output = result.stdout
    body_match = re.search(r"<body[^>]*>(.*)</body>", output, re.S)
    content = body_match.group(1).strip() if body_match else output
    toc_match = re.search(r'<nav id="TOC".*?</nav>', content, re.S)
    toc = toc_match.group(0) if toc_match else ""
    if toc:
        content = content.replace(toc, "", 1)
    return content.strip(), toc


def rel_link(target_url: str, current_url: str) -> str:
    return os.path.relpath(PAGES / target_url, start=(PAGES / current_url).parent).replace(os.sep, "/")


def rewrite_links(body: str, source: Path, current_url: str, path_map: dict) -> str:
    def replace(match):
        target, anchor = match.group(1), match.group(2) or ""
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        resolved = (source.parent / target).resolve()
        info = path_map.get(str(resolved))
        if not info:
            return match.group(0)
        return f"]({rel_link(info['url'], current_url)}{anchor})"

    return re.sub(r"\]\(([^)\s]+?\.md)(#[^)]*)?\)", replace, body)


def page_shell(title: str, body: str, root: str, current: str, toc: str = "", extra_class: str = "") -> str:
    modules = json.loads((LIB / "data" / "nav.json").read_text(encoding="utf-8"))["modules"]
    nav_items = []
    for module in modules:
        active = " active" if current == f"module/{module['id']}.html" else ""
        nav_items.append(
            f'<a class="nav-item{active}" href="{root}module/{module["id"]}.html">'
            f'<span class="nav-icon">{module["icon"]}</span>{html.escape(module["title"])}</a>'
        )
    toc_html = f'<aside class="toc"><div class="toc-title">本页目录</div>{toc}</aside>' if toc else '<aside class="toc"></aside>'
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(SITE_SUBTITLE)}">
<title>{html.escape(title)} · {SITE_TITLE}</title>
<link rel="stylesheet" href="{root}assets/css/site.css">
</head>
<body data-root="{root}">
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <a class="brand" href="{root}index.html">
      <span class="brand-mark">营</span>
      <span><strong>{SITE_TITLE}</strong><small>Nutrition Library</small></span>
    </a>
    <div class="search-box">
      <input id="search-input" type="search" placeholder="搜索主题、标签、正文…" autocomplete="off">
      <div id="search-results" class="search-results"></div>
    </div>
    <nav class="nav">
      <div class="nav-group">入口</div>
      <a class="nav-item" href="{root}index.html"><span class="nav-icon">🏠</span>首页</a>
      <a class="nav-item" href="{root}master-index.html"><span class="nav-icon">🗂️</span>总目录</a>
      <a class="nav-item" href="{root}learning-paths.html"><span class="nav-icon">🧭</span>学习路径</a>
      <a class="nav-item" href="{root}glossary.html"><span class="nav-icon">📖</span>术语表</a>
      <div class="nav-group">14 个模块</div>
      {''.join(nav_items)}
    </nav>
    <div class="sidebar-foot">v1.0 · 68 个主题初稿</div>
  </aside>
  <main class="main {extra_class}" id="main">
    <div class="topbar">
      <button class="menu-toggle" id="menu-toggle" aria-label="打开导航">☰</button>
      <span class="crumb">{html.escape(title)}</span>
    </div>
    {body}
  </main>
  {toc_html}
</div>
<script src="{root}assets/js/search-data.js"></script>
<script src="{root}assets/js/site.js"></script>
</body>
</html>
"""


def article_pager(index: int, articles: list, root: str) -> str:
    prev_link = next_link = ""
    if index > 0:
        prev = articles[index - 1]
        prev_link = f'<a class="pager-prev" href="{root}topic/{prev["slug"]}.html"><small>上一篇</small><span>{html.escape(prev["title"])}</span></a>'
    if index < len(articles) - 1:
        nxt = articles[index + 1]
        next_link = f'<a class="pager-next" href="{root}topic/{nxt["slug"]}.html"><small>下一篇</small><span>{html.escape(nxt["title"])}</span></a>'
    return f'<nav class="pager">{prev_link}{next_link}</nav>'


def main():
    nav = json.loads((LIB / "data" / "nav.json").read_text(encoding="utf-8"))
    modules = nav["modules"]
    PAGES.mkdir(parents=True, exist_ok=True)
    (PAGES / "module").mkdir(exist_ok=True)
    (PAGES / "topic").mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "css").mkdir(exist_ok=True)
    (ASSETS / "js").mkdir(exist_ok=True)

    overview = [
        {
            "title": "总目录",
            "slug": "master-index",
            "path": LIB / "00-总览" / "00-总目录.md",
            "summary": "14 个模块、68 个主题的全景目录。",
            "tags": ["导航", "总目录"],
        },
        {
            "title": "学习路径",
            "slug": "learning-paths",
            "path": LIB / "00-总览" / "01-学习路径.md",
            "summary": "零基础、减重、家庭健康、从业进阶四条路径。",
            "tags": ["导航", "学习"],
        },
        {
            "title": "术语表",
            "slug": "glossary",
            "path": LIB / "00-总览" / "02-术语表.md",
            "summary": "营养学核心术语速查。",
            "tags": ["术语", "工具"],
        },
    ]

    articles = []
    for module in modules:
        for topic in module["topics"]:
            articles.append(
                {
                    "title": topic["title"],
                    "slug": topic["slug"],
                    "summary": topic.get("coreQuestion", ""),
                    "tags": [module["title"]],
                    "path": LIB / topic["plannedPath"],
                    "module_id": module["id"],
                    "module_title": module["title"],
                    "order": topic["order"],
                    "status": topic.get("status", "planned"),
                    "url": f"topic/{topic['slug']}.html",
                }
            )

    path_map = {}
    for article in articles:
        path_map[str(article["path"].resolve())] = {"url": article["url"]}
    for module in modules:
        path_map[str((LIB / module["guide"]).resolve())] = {"url": f"module/{module['id']}.html"}
    for item in overview:
        path_map[str(item["path"].resolve())] = {"url": f"{item['slug']}.html"}

    search_index = []
    total_chars = 0

    # 文章页
    for i, article in enumerate(articles):
        raw = article["path"].read_text(encoding="utf-8")
        meta, body = frontmatter(raw)
        article["summary"] = meta.get("summary", article["summary"])
        article["tags"] = [x.strip() for x in meta.get("tags", "").strip("[]").split(",") if x.strip()]
        article["status"] = meta.get("status", article["status"])
        total_chars += len(body)
        body = re.sub(r"^# .+\n", "", body, count=1, flags=re.M)
        body = rewrite_links(body, article["path"], article["url"], path_map)
        content, toc = pandoc_convert(body)
        body_html = f"""
<article class="article">
  <div class="article-meta"><a href="../module/{article['module_id']}.html">{html.escape(article['module_title'])}</a>
  <span class="badge badge-{article['status']}">{STATUS_LABEL.get(article['status'], article['status'])}</span></div>
  <h1>{html.escape(article['title'])}</h1>
  <p class="lede">{html.escape(article['summary'])}</p>
  <div class="prose">{content}</div>
  {article_pager(i, articles, '../')}
</article>"""
        search_index.append(
            {
                "title": article["title"],
                "url": article["url"],
                "module": article["module_title"],
                "summary": article["summary"],
                "tags": article["tags"],
                "text": strip_markdown(body)[:3000],
            }
        )
        (PAGES / "topic" / f"{article['slug']}.html").write_text(
            page_shell(article["title"], body_html, "../", article["url"], toc), encoding="utf-8"
        )

    # 模块页
    for module in modules:
        guide_path = LIB / module["guide"]
        raw = guide_path.read_text(encoding="utf-8")
        _, body = frontmatter(raw)
        body = re.sub(r"^# .+\n", "", body, count=1, flags=re.M)
        body = rewrite_links(body, guide_path, f"module/{module['id']}.html", path_map)
        content, toc = pandoc_convert(body)
        cards = []
        for topic in module["topics"]:
            cards.append(
                f'<a class="topic-card" href="../topic/{topic["slug"]}.html">'
                f'<span class="topic-num">{topic["order"]:02d}</span>'
                f'<span class="topic-title">{html.escape(topic["title"])}</span>'
                f'<span class="topic-q">{html.escape(topic.get("coreQuestion", ""))}</span>'
                f'<span class="badge badge-{topic.get("status", "planned")}">{"初稿" if topic.get("status")=="draft" else "待补充"}</span>'
                f"</a>"
            )
        body_html = f"""
<article class="article">
  <div class="article-meta">模块 {module['order']:02d} · {len(module['topics'])} 个主题</div>
  <h1><span class="h1-icon">{module['icon']}</span>{html.escape(module['title'])}</h1>
  <p class="lede">{html.escape(module['position'])}</p>
  <div class="outcome"><strong>学完能做到</strong><br>{html.escape(module['outcome'])}</div>
  <h2 class="section-title">主题清单</h2>
  <div class="topic-grid">{''.join(cards)}</div>
  <details class="guide-details"><summary>模块说明、参考来源与写作约定</summary><div class="prose">{content}</div></details>
</article>"""
        (PAGES / "module" / f"{module['id']}.html").write_text(
            page_shell(module["title"], body_html, "../", f"module/{module['id']}.html", toc), encoding="utf-8"
        )

    # 总览页
    for item in overview:
        raw = item["path"].read_text(encoding="utf-8")
        meta, body = frontmatter(raw)
        body = re.sub(r"^# .+\n", "", body, count=1, flags=re.M)
        body = rewrite_links(body, item["path"], f"{item['slug']}.html", path_map)
        content, toc = pandoc_convert(body)
        body_html = f"""
<article class="article">
  <div class="article-meta">总览</div>
  <h1>{html.escape(meta.get('title', item['title']))}</h1>
  <p class="lede">{html.escape(item['summary'])}</p>
  <div class="prose">{content}</div>
</article>"""
        (PAGES / f"{item['slug']}.html").write_text(
            page_shell(item["title"], body_html, "", f"{item['slug']}.html", toc), encoding="utf-8"
        )
        search_index.append(
            {
                "title": item["title"],
                "url": f"{item['slug']}.html",
                "module": "总览",
                "summary": item["summary"],
                "tags": item["tags"],
                "text": strip_markdown(body)[:2000],
            }
        )

    # 首页
    cards = []
    for module in modules:
        count = len(module["topics"])
        reviewed = sum(1 for t in module["topics"] if t.get("status") == "review")
        cards.append(
            f'<a class="module-card" href="module/{module["id"]}.html">'
            f'<div class="module-icon">{module["icon"]}</div>'
            f'<div class="module-body"><h3>{html.escape(module["title"])}</h3>'
            f'<p>{html.escape(module["position"])}</p>'
            f'<div class="module-meta"><span>{count} 个主题</span><span class="dot">·</span><span>{reviewed} 篇审校中 / {count} 篇初稿</span></div></div>'
            f'<span class="module-arrow">→</span></a>'
        )
    home_body = f"""
<section class="hero">
  <div class="hero-kicker">NUTRITION LIBRARY · v1.0</div>
  <h1>{SITE_TITLE}</h1>
  <p class="hero-sub">{SITE_SUBTITLE}</p>
  <div class="hero-stats">
    <div><strong>14</strong><span>模块</span></div>
    <div><strong>68</strong><span>主题</span></div>
    <div><strong>{total_chars:,}</strong><span>字符</span></div>
    <div><strong>100%</strong><span>初稿覆盖</span></div>
  </div>
  <div class="hero-actions">
    <a class="btn btn-primary" href="learning-paths.html">选择学习路径</a>
    <a class="btn" href="master-index.html">浏览总目录</a>
    <a class="btn btn-ghost" href="glossary.html">查术语</a>
  </div>
</section>
<section class="home-section">
  <div class="section-head"><h2>14 个模块</h2><p>从基础营养学到临床、循证与实操工具</p></div>
  <div class="module-grid">{''.join(cards)}</div>
</section>
<section class="home-section">
  <div class="section-head"><h2>怎么用</h2><p>先建立框架，再按问题深入</p></div>
  <div class="how-grid">
    <div class="how-card"><span>01</span><h3>零基础</h3><p>从 01 营养学基础开始，按学习路径 A 走一遍。</p><a href="learning-paths.html">看路径 →</a></div>
    <div class="how-card"><span>02</span><h3>减重</h3><p>直接看 06 能量平衡与体重管理，配合 13 实操工具。</p><a href="module/weight.html">进入模块 →</a></div>
    <div class="how-card"><span>03</span><h3>给家人</h3><p>07 生命周期营养 + 09 疾病营养，按人群查。</p><a href="module/lifecycle.html">进入模块 →</a></div>
    <div class="how-card"><span>04</span><h3>辨别信息</h3><p>12 循证营养与辟谣，学会看研究类型和证据等级。</p><a href="module/evidence.html">进入模块 →</a></div>
  </div>
</section>"""
    (PAGES / "index.html").write_text(page_shell("首页", home_body, "", "index.html", extra_class="home"), encoding="utf-8")

    # 搜索索引
    (ASSETS / "js" / "search-data.js").write_text(
        "window.SEARCH_INDEX = " + json.dumps(search_index, ensure_ascii=False) + ";\n", encoding="utf-8"
    )

    # 样式与脚本
    (ASSETS / "css" / "site.css").write_text(SITE_CSS, encoding="utf-8")
    (ASSETS / "js" / "site.js").write_text(SITE_JS, encoding="utf-8")
    (PAGES / ".gitkeep").touch()

    print(f"构建完成：{len(articles)} 篇文章，{len(modules)} 个模块，{len(overview)} 个总览页。")
    print(f"总字符：{total_chars:,}")


SITE_CSS = r"""
:root{
  --ink:#1c2723; --muted:#66736c; --line:#e3e6df; --bg:#fbfaf6; --panel:#ffffff;
  --green:#1f5c4a; --green-soft:#e8f0eb; --accent:#c97b3d; --accent-soft:#f7ecdf;
  --sidebar:280px; --toc:230px; --max:860px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.8;-webkit-font-smoothing:antialiased}
a{color:var(--green);text-decoration:none}
a:hover{text-decoration:underline}
.layout{display:grid;grid-template-columns:var(--sidebar) minmax(0,1fr) var(--toc);min-height:100vh;max-width:1600px;margin:0 auto}
.sidebar{position:sticky;top:0;height:100vh;overflow-y:auto;padding:26px 20px 30px;border-right:1px solid var(--line);background:linear-gradient(180deg,#f7f5ee, #fbfaf6)}
.brand{display:flex;gap:12px;align-items:center;margin-bottom:22px;color:var(--ink)}
.brand:hover{text-decoration:none}
.brand-mark{width:42px;height:42px;border-radius:12px;background:var(--green);color:#fff;display:grid;place-items:center;font-size:20px;font-weight:700;box-shadow:0 6px 16px rgba(31,92,74,.22)}
.brand strong{display:block;font-size:17px;letter-spacing:.5px}
.brand small{display:block;color:var(--muted);font-size:10px;letter-spacing:1.4px;text-transform:uppercase}
.search-box{position:relative;margin-bottom:20px}
#search-input{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;font-size:13px;color:var(--ink);outline:none}
#search-input:focus{border-color:var(--green);box-shadow:0 0 0 3px var(--green-soft)}
.search-results{display:none;position:absolute;z-index:40;left:0;right:0;top:calc(100% + 6px);background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 16px 40px rgba(20,40,30,.14);max-height:420px;overflow:auto}
.search-results.open{display:block}
.search-hit{display:block;padding:10px 12px;border-bottom:1px solid #f0f1ec}
.search-hit:last-child{border-bottom:0}
.search-hit:hover{background:#f7f8f3;text-decoration:none}
.search-hit b{display:block;font-size:13px;color:var(--ink)}
.search-hit span{display:block;font-size:11px;color:var(--muted);margin-top:2px}
.search-empty{padding:12px;font-size:12px;color:var(--muted)}
.nav-group{font-size:10px;letter-spacing:1.6px;text-transform:uppercase;color:#9aa39d;margin:18px 8px 8px}
.nav-item{display:flex;align-items:center;gap:9px;padding:7px 9px;border-radius:8px;font-size:13.5px;color:#33423a;line-height:1.4}
.nav-item:hover{background:#eef1e9;text-decoration:none}
.nav-item.active{background:var(--green-soft);color:var(--green);font-weight:600}
.nav-icon{width:20px;text-align:center;font-size:14px}
.sidebar-foot{margin-top:26px;padding-top:16px;border-top:1px solid var(--line);font-size:11px;color:#9aa39d}
.main{padding:0 46px 70px;min-width:0}
.main.home{grid-column:2/4}
.toc:empty{display:none}
.topbar{display:flex;align-items:center;gap:14px;height:58px;border-bottom:1px solid var(--line);margin-bottom:34px;color:var(--muted);font-size:12px}
.menu-toggle{display:none;border:1px solid var(--line);background:#fff;border-radius:8px;width:34px;height:34px;font-size:16px;cursor:pointer}
.crumb{letter-spacing:.4px}
.article{max-width:var(--max);margin:0 auto}
.article-meta{font-size:12px;color:var(--muted);letter-spacing:.4px;margin-bottom:6px}
.article-meta a{color:var(--green)}
.article h1{font-size:36px;line-height:1.3;margin:6px 0 12px;letter-spacing:-.5px}
.h1-icon{margin-right:8px}
.lede{font-size:16px;color:#5a675f;margin:0 0 28px;padding-left:14px;border-left:3px solid var(--accent)}
.outcome{background:var(--green-soft);border:1px solid #d6e4da;border-radius:12px;padding:16px 18px;font-size:14px;margin:22px 0 30px}
.section-title{font-size:20px;margin:34px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.prose{font-size:15.5px;line-height:1.9}
.prose h2{font-size:24px;margin:40px 0 12px;padding-bottom:6px;border-bottom:1px solid #eceee7;letter-spacing:-.2px}
.prose h3{font-size:18.5px;margin:28px 0 8px;color:#234438}
.prose p{margin:12px 0}
.prose ul,.prose ol{padding-left:22px;margin:10px 0}
.prose li{margin:5px 0}
.prose blockquote{margin:18px 0;padding:12px 18px;background:var(--accent-soft);border-left:3px solid var(--accent);color:#5b4632;border-radius:0 8px 8px 0}
.prose blockquote p{margin:4px 0}
.prose table{width:100%;border-collapse:collapse;margin:18px 0;font-size:14px;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}
.prose th{background:#f2f4ee;text-align:left;font-weight:600;color:#33423a;padding:10px 12px;border-bottom:1px solid var(--line)}
.prose td{padding:9px 12px;border-bottom:1px solid #eef0e9;vertical-align:top}
.prose tr:last-child td{border-bottom:0}
.prose tr:nth-child(even) td{background:#fcfcf9}
.prose code{background:#eef1e9;padding:2px 5px;border-radius:4px;font-size:.9em;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.prose pre{background:#1f2a25;color:#e7efe9;padding:16px;border-radius:10px;overflow:auto;font-size:13px}
.prose pre code{background:none;color:inherit;padding:0}
.prose hr{border:0;border-top:1px solid var(--line);margin:34px 0}
.prose img{max-width:100%;border-radius:10px}
.badge{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:999px;font-size:10px;letter-spacing:.5px;vertical-align:1px}
.badge-draft{background:var(--accent-soft);color:#8a4f1d}
.badge-published{background:var(--green-soft);color:var(--green)}
.badge-planned{background:#eef0e9;color:#8b938d}
.pager{display:flex;justify-content:space-between;gap:20px;margin-top:52px;padding-top:24px;border-top:1px solid var(--line)}
.pager a{display:flex;flex-direction:column;gap:4px;max-width:46%;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:#fff}
.pager a:hover{border-color:var(--green);text-decoration:none}
.pager small{color:var(--muted);font-size:10px;letter-spacing:1px}
.pager span{font-size:13px;color:var(--ink)}
.pager-next{margin-left:auto;text-align:right}
.toc{position:sticky;top:0;height:100vh;overflow-y:auto;padding:76px 24px 40px 10px;font-size:12px;color:var(--muted)}
.toc-title{font-size:10px;letter-spacing:1.6px;text-transform:uppercase;color:#9aa39d;margin-bottom:10px}
.toc nav#TOC ul{list-style:none;padding-left:0;margin:0}
.toc nav#TOC ul ul{padding-left:12px;margin-top:4px}
.toc nav#TOC li{margin:5px 0;line-height:1.5}
.toc nav#TOC a{color:#6b7770;display:block;border-left:2px solid transparent;padding-left:8px}
.toc nav#TOC a:hover{color:var(--green);border-left-color:var(--green);text-decoration:none}
.topic-grid{display:grid;gap:10px;margin:18px 0 30px}
.topic-card{display:grid;grid-template-columns:44px 1fr auto;grid-template-rows:auto auto;column-gap:12px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;color:var(--ink);transition:.16s}
.topic-card:hover{border-color:#c8d6cc;box-shadow:0 8px 20px rgba(31,92,74,.07);text-decoration:none;transform:translateY(-1px)}
.topic-num{grid-row:1/3;font-size:18px;color:#b6bdb6;font-variant-numeric:tabular-nums}
.topic-title{font-weight:600;font-size:15px}
.topic-q{grid-column:2/3;font-size:12px;color:var(--muted);line-height:1.5}
.topic-card .badge{grid-column:3;grid-row:1/3}
.guide-details{margin:34px 0;border:1px solid var(--line);border-radius:12px;background:#fff;padding:14px 18px}
.guide-details summary{cursor:pointer;font-weight:600;color:#33423a;font-size:14px}
.guide-details[open] summary{margin-bottom:8px}
.hero{padding:54px 0 40px;border-bottom:1px solid var(--line)}
.hero-kicker{font-size:10px;letter-spacing:3px;color:var(--accent);font-weight:600;margin-bottom:12px}
.hero h1{font-size:58px;line-height:1.1;margin:0 0 14px;letter-spacing:-1.5px;color:#173f33}
.hero-sub{font-size:18px;color:#5a675f;margin:0 0 30px}
.hero-stats{display:flex;gap:38px;margin:26px 0 30px;flex-wrap:wrap}
.hero-stats div{display:flex;flex-direction:column}
.hero-stats strong{font-size:26px;color:var(--green);font-variant-numeric:tabular-nums}
.hero-stats span{font-size:11px;letter-spacing:1.2px;color:var(--muted);text-transform:uppercase}
.hero-actions{display:flex;gap:10px;flex-wrap:wrap}
.btn{display:inline-block;padding:10px 16px;border:1px solid var(--line);border-radius:999px;background:#fff;color:#33423a;font-size:13px}
.btn:hover{text-decoration:none;border-color:#c8d6cc}
.btn-primary{background:var(--green);border-color:var(--green);color:#fff}
.btn-primary:hover{background:#194b3d}
.btn-ghost{background:transparent}
.home-section{padding:38px 0 10px}
.section-head{display:flex;align-items:baseline;justify-content:space-between;gap:20px;margin-bottom:18px}
.section-head h2{font-size:24px;margin:0}
.section-head p{color:var(--muted);font-size:13px;margin:0}
.module-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.module-card{display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;color:var(--ink);transition:.16s}
.module-card:hover{border-color:#c8d6cc;box-shadow:0 10px 26px rgba(31,92,74,.08);text-decoration:none;transform:translateY(-1px)}
.module-icon{font-size:24px;line-height:1.2}
.module-body{flex:1;min-width:0}
.module-body h3{margin:0 0 4px;font-size:15.5px}
.module-body p{margin:0 0 8px;font-size:12.5px;color:var(--muted);line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.module-meta{font-size:11px;color:#8b938d}
.module-meta .dot{margin:0 5px}
.module-arrow{color:#b6bdb6;font-size:16px;align-self:center}
.how-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.how-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px}
.how-card span{font-size:11px;letter-spacing:1.4px;color:var(--accent)}
.how-card h3{margin:6px 0 6px;font-size:15px}
.how-card p{margin:0 0 10px;font-size:12.5px;color:var(--muted);line-height:1.6}
.how-card a{font-size:12px}
@media(max-width:1280px){.layout{grid-template-columns:var(--sidebar) minmax(0,1fr)}.toc{display:none}.main{padding-right:40px}.main.home{grid-column:2/3}}
@media(max-width:960px){.module-grid{grid-template-columns:1fr}.how-grid{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:46px}}
@media(max-width:760px){
  .layout{display:block}
  .sidebar{position:fixed;z-index:60;left:0;top:0;width:86%;max-width:320px;transform:translateX(-105%);transition:.22s;box-shadow:0 0 60px rgba(0,0,0,.18)}
  .sidebar.open{transform:translateX(0)}
  .main{padding:0 20px 60px}
  .menu-toggle{display:block}
  .topbar{height:52px;margin-bottom:24px}
  .article h1{font-size:30px}
  .hero{padding-top:30px}.hero h1{font-size:38px}.hero-stats{gap:22px}
  .prose{font-size:15px}
  .prose table{display:block;overflow-x:auto;white-space:nowrap}
  .pager{flex-direction:column}.pager a{max-width:100%}.pager-next{text-align:left}
  .how-grid{grid-template-columns:1fr}
}
@media print{
  .sidebar,.toc,.topbar,.pager,.search-box{display:none!important}
  .layout{display:block}.main{padding:0}.article{max-width:none}
  body{background:#fff}.prose table{page-break-inside:avoid}
}
"""

SITE_JS = r"""
(function(){
  const menuBtn = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  if(menuBtn && sidebar){
    menuBtn.addEventListener('click',()=>sidebar.classList.toggle('open'));
    document.addEventListener('click',(e)=>{
      if(window.innerWidth<=760 && sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target!==menuBtn){
        sidebar.classList.remove('open');
      }
    });
  }
  const input = document.getElementById('search-input');
  const box = document.getElementById('search-results');
  if(!input || !box || !window.SEARCH_INDEX) return;
  const root = document.body.dataset.root || '';
  function escapeHtml(s){return s.replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));}
  function render(){
    const q = input.value.trim().toLowerCase();
    if(q.length < 1){box.classList.remove('open');box.innerHTML='';return;}
    const hits = window.SEARCH_INDEX.filter(item=>{
      const hay = (item.title+' '+item.summary+' '+(item.tags||[]).join(' ')+' '+item.text).toLowerCase();
      return hay.includes(q);
    }).slice(0,9);
    if(!hits.length){box.innerHTML='<div class="search-empty">没有找到，试试“蛋白质”“减重”“维生素 D”。</div>';box.classList.add('open');return;}
    box.innerHTML = hits.map(item=>`<a class="search-hit" href="${root}${item.url}"><b>${escapeHtml(item.title)}</b><span>${escapeHtml(item.module)} · ${escapeHtml(item.summary||'')}</span></a>`).join('');
    box.classList.add('open');
  }
  input.addEventListener('input', render);
  input.addEventListener('focus', render);
  document.addEventListener('click',(e)=>{if(!box.contains(e.target)&&e.target!==input)box.classList.remove('open');});
  document.addEventListener('keydown',(e)=>{if(e.key==='Escape'){box.classList.remove('open');input.blur();}});
})();
"""


if __name__ == "__main__":
    main()
