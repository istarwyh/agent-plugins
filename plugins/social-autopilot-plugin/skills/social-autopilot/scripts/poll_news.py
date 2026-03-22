import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests
from loguru import logger

from common import load_context, init_db, ensure_dirs, get_db
from models import NewsItem


def compute_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def fetch_source(source: dict, timeout: int = 15) -> list[NewsItem]:
    items = []
    for rss_url in source["urls"]:
        try:
            resp = requests.get(rss_url, timeout=timeout, headers={
                "User-Agent": "Mozilla/5.0 (compatible; SocialAutopilot/1.0)"
            })
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)

            if feed.bozo and not feed.entries:
                logger.warning(f"[{source['id']}] RSS解析异常: {feed.bozo_exception}")
                continue

            for entry in feed.entries:
                url = entry.get("link", "")
                if not url:
                    continue

                title = entry.get("title", "").strip()
                summary = entry.get("summary", "")[:500].strip()

                pub = entry.get("published_parsed")
                published_at = datetime(*pub[:6], tzinfo=timezone.utc) if pub else None

                text_lower = f"{title} {summary}".lower()
                whitelist = source.get("keywords_whitelist", [])
                blacklist = source.get("keywords_blacklist", [])

                if whitelist and not any(kw.lower() in text_lower for kw in whitelist):
                    continue
                if any(kw.lower() in text_lower for kw in blacklist):
                    continue

                items.append(NewsItem(
                    url=url,
                    url_hash=compute_hash(url),
                    title=title,
                    summary=summary,
                    published_at=published_at,
                    source_id=source["id"],
                    category=source["category"],
                ))
        except requests.RequestException as e:
            logger.warning(f"[{source['id']}] 请求失败 {rss_url}: {e}")
        except Exception as e:
            logger.error(f"[{source['id']}] 错误: {e}")

    logger.info(f"[{source['id']}] 匹配 {len(items)} 条新闻")
    return items


def filter_new(items: list[NewsItem], db_path: Path) -> list[NewsItem]:
    if not items:
        return []
    hashes = [i.url_hash for i in items]
    with get_db(db_path) as conn:
        placeholders = ",".join("?" * len(hashes))
        rows = conn.execute(
            f"SELECT url_hash FROM processed_news WHERE url_hash IN ({placeholders})",
            hashes,
        ).fetchall()
        existing = {row["url_hash"] for row in rows}
    new = [i for i in items if i.url_hash not in existing]
    logger.info(f"去重: {len(items)} → {len(new)} 条")
    return new


def mark_processed(items: list[NewsItem], db_path: Path):
    if not items:
        return
    with get_db(db_path) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO processed_news (url_hash, url, title, source_id, category) VALUES (?,?,?,?,?)",
            [(i.url_hash, i.url, i.title, i.source_id, i.category) for i in items],
        )


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RSS新闻抓取")
    parser.add_argument("--priority", choices=["high", "medium", "low"])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(args)


def main(args: list[str] = None) -> list[NewsItem]:
    if args is None:
        args = []
    opts = parse_args(args)
    ctx = load_context(dry_run=opts.dry_run)
    init_db(ctx.db_path)
    ensure_dirs()

    sources = ctx.config.get("sources", [])
    if opts.priority:
        sources = [s for s in sources if s["priority"] == opts.priority]

    start = time.time()
    all_items = []
    for source in sources:
        all_items.extend(fetch_source(source))

    new_items = filter_new(all_items, ctx.db_path)

    if not opts.dry_run:
        mark_processed(new_items, ctx.db_path)

    # Save new items to JSON
    if new_items:
        output_dir = ctx.work_dir / "output" / "news"
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_file = output_dir / f"news_{ts}.json"
        out_file.write_text(json.dumps(
            [item.model_dump(mode="json") for item in new_items],
            ensure_ascii=False, indent=2,
        ))

    duration = int((time.time() - start) * 1000)
    print(f"抓取完成: {len(all_items)} 条匹配, {len(new_items)} 条新增, 耗时 {duration}ms")
    return new_items


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
