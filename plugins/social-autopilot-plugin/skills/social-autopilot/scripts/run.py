import argparse
import importlib
import sys
from pathlib import Path

CHANNEL_ALIASES = {
    "xhs": "xiaohongshu",
    "red": "xiaohongshu",
}

SCRIPTS = {
    "setup.py": "setup",
    "poll_news.py": "poll_news",
    "generate_posts.py": "generate_posts",
    "generate_card.py": "generate_card",
    "generate_ai_covers.py": "generate_ai_covers",
    "schedule_meta.py": "schedule_meta",
    "publish_channels.py": "publish_channels",
    "install_cron.py": "install_cron",
    "status.py": "status",
    "pipeline": "pipeline",
}


def run_pipeline(args: list[str]):
    """Run full pipeline: poll → generate posts → generate cards → publish channels."""
    from common import load_context, init_db, ensure_dirs, get_db

    opts = _parse_pipeline_args(args)
    ctx = load_context(dry_run=opts.dry_run)
    init_db(ctx.db_path)
    ensure_dirs()

    pass_args = ["--dry-run"] if opts.dry_run else []
    generate_args = [*pass_args]
    channel = _normalize_channel(opts.channel) if opts.channel else None
    if channel:
        generate_args.extend(["--channel", channel])
    if opts.limit is not None:
        generate_args.extend(["--limit", str(opts.limit)])
    if opts.skip_preflight:
        generate_args.append("--skip-preflight")

    publish_args = [*pass_args, "--limit", str(opts.publish_limit or opts.limit or ctx.max_posts)]
    if opts.xhs_publish_mode:
        publish_args.extend(["--xhs-publish-mode", opts.xhs_publish_mode])

    print("=== 第1步: 抓取新闻 ===")
    poll = importlib.import_module("poll_news")
    news_items = poll.main(pass_args)

    if not news_items:
        print("无新增新闻，流程结束。")
        return

    print(f"\n=== 第2步: 生成帖子 ({len(news_items)} 条新闻) ===")
    gen = importlib.import_module("generate_posts")
    drafts = gen.main(generate_args)

    if not drafts:
        print("未生成帖子。")
        if opts.dry_run and not opts.no_publish:
            _run_publish_stage(publish_args, channel)
            print("\n=== 流程完成 ===")
        else:
            print("流程结束。")
        return

    if opts.ai_covers:
        _run_ai_cover_stage(opts, channel)

    print(f"\n=== 第3步: 生成卡片图 ({len(drafts)} 条平台草稿) ===")
    card = importlib.import_module("generate_card")
    seen = set()
    for draft in drafts:
        if _draft_has_card_path(get_db, ctx, draft):
            continue
        key = draft.brief_id or draft.news_url
        if key in seen:
            continue
        seen.add(key)
        card_path = card.generate_single_card(
            title=draft.platform_title or draft.news_title,
            category=draft.category,
            brand_color=_get_brand_color(ctx, draft.category),
            output_dir=ctx.work_dir / "output" / "cards",
            dry_run=opts.dry_run,
        )
        if card_path:
            _update_card_path(get_db, ctx, draft, card_path)

    if opts.no_publish:
        print("\n=== 第4步: 已跳过渠道发布/草稿生成 (--no-publish) ===")
    else:
        _run_publish_stage(publish_args, channel)

    print("\n=== 流程完成 ===")


def _parse_pipeline_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="全链路运行: 抓取新闻 → 生成帖子 → 生成卡片 → 渠道处理")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--channel", choices=["meta", "xiaohongshu", "xhs", "red"], help="临时指定目标渠道，不依赖 config.json enabled")
    parser.add_argument("--limit", type=int, help="本次最多生成多少条新闻内容，默认使用 MAX_POSTS_PER_RUN")
    parser.add_argument("--publish-limit", type=int, help="本次每个渠道最多处理多少条待发布草稿")
    parser.add_argument("--skip-preflight", action="store_true", help="跳过 LLM 模型连通性预检")
    parser.add_argument("--no-publish", action="store_true", help="只生成新闻/帖子/卡片，不进入渠道发布阶段")
    parser.add_argument("--ai-covers", action="store_true", help="用 codex-image/Codex CLI 为小红书草稿生成高质量 AI 封面")
    parser.add_argument("--ai-cover-limit", type=int, help="本次最多生成几张 AI 封面")
    parser.add_argument("--ai-cover-size", default="1024x1536", choices=["1024x1024", "1024x1536", "1536x1024", "auto"])
    parser.add_argument("--ai-cover-quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument(
        "--xhs-publish-mode",
        choices=["draft", "publish"],
        help="覆盖小红书发布模式：draft=只填表，publish=直接发布",
    )
    return parser.parse_args(args)


def _normalize_channel(channel: str) -> str:
    return CHANNEL_ALIASES.get(str(channel).lower(), channel)


def _run_ai_cover_stage(opts: argparse.Namespace, channel: str | None):
    print("\n=== 第3步前置: 生成 AI 封面 (codex-image) ===")
    cover = importlib.import_module("generate_ai_covers")
    platform = channel or "xiaohongshu"
    args = ["--platform", platform, "--limit", str(opts.ai_cover_limit or opts.limit or 3)]
    args.extend(["--size", opts.ai_cover_size, "--quality", opts.ai_cover_quality])
    if opts.dry_run:
        args.append("--dry-run")
    cover.main(args)


def _run_publish_stage(pass_args: list[str], channel: str | None = None):
    print("\n=== 第4步: 渠道发布/草稿生成 ===")
    publisher = importlib.import_module("publish_channels")
    if channel:
        publisher.main(["--channel", channel, *pass_args])
    else:
        publisher.main(["--enabled", *pass_args])


def _get_brand_color(ctx, category: str) -> str:
    for source in ctx.config.get("sources", []):
        if source["category"] == category:
            return source.get("brand_color", "#333333")
    return "#333333"


def _draft_has_card_path(get_db, ctx, draft) -> bool:
    with get_db(ctx.db_path) as conn:
        row = conn.execute(
            "SELECT card_path FROM post_drafts WHERE news_url=? AND platform=? AND status='pending' ORDER BY id DESC LIMIT 1",
            (draft.news_url, draft.platform),
        ).fetchone()
    return bool(row and row["card_path"])


def _update_card_path(get_db, ctx, draft, card_path: Path):
    with get_db(ctx.db_path) as conn:
        if draft.brief_id:
            conn.execute(
                """
                UPDATE post_drafts
                SET card_path=?
                WHERE brief_id=? AND status='pending' AND (card_path IS NULL OR card_path='')
                """,
                (str(card_path), draft.brief_id),
            )
        else:
            conn.execute(
                """
                UPDATE post_drafts
                SET card_path=?
                WHERE news_url=? AND status='pending' AND (card_path IS NULL OR card_path='')
                """,
                (str(card_path), draft.news_url),
            )


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/run.py <脚本> [参数...]")
        print("\n可用脚本:")
        for key in SCRIPTS:
            print(f"  {key}")
        sys.exit(1)

    script = sys.argv[1]
    mod_name = SCRIPTS.get(script) or SCRIPTS.get(f"{script}.py")

    if not mod_name:
        print(f"未知脚本: {script}")
        print("可选:")
        for key in SCRIPTS:
            print(f"  {key}")
        sys.exit(1)

    if mod_name == "pipeline":
        run_pipeline(sys.argv[2:])
        return

    sys.path.append(str(Path(__file__).resolve().parent))
    module = importlib.import_module(mod_name)
    module.main(sys.argv[2:])


if __name__ == "__main__":
    main()
