import importlib
import sys
from pathlib import Path

SCRIPTS = {
    "setup.py": "setup",
    "poll_news.py": "poll_news",
    "generate_posts.py": "generate_posts",
    "generate_card.py": "generate_card",
    "schedule_meta.py": "schedule_meta",
    "publish_channels.py": "publish_channels",
    "install_cron.py": "install_cron",
    "status.py": "status",
    "pipeline": "pipeline",
}


def run_pipeline(args: list[str]):
    """Run full pipeline: poll → generate posts → generate cards → publish channels."""
    from common import load_context, init_db, ensure_dirs, get_db

    dry_run = "--dry-run" in args
    ctx = load_context(dry_run=dry_run)
    init_db(ctx.db_path)
    ensure_dirs()

    pass_args = ["--dry-run"] if dry_run else []

    print("=== 第1步: 抓取新闻 ===")
    poll = importlib.import_module("poll_news")
    news_items = poll.main(pass_args)

    if not news_items:
        print("无新增新闻，流程结束。")
        return

    print(f"\n=== 第2步: 生成帖子 ({len(news_items)} 条新闻) ===")
    gen = importlib.import_module("generate_posts")
    drafts = gen.main(pass_args)

    if not drafts:
        print("未生成帖子。")
        if dry_run:
            _run_publish_stage(pass_args)
            print("\n=== 流程完成 ===")
        else:
            print("流程结束。")
        return

    print(f"\n=== 第3步: 生成卡片图 ({len(drafts)} 条平台草稿) ===")
    card = importlib.import_module("generate_card")
    seen = set()
    for draft in drafts:
        key = draft.brief_id or draft.news_url
        if key in seen:
            continue
        seen.add(key)
        card_path = card.generate_single_card(
            title=draft.platform_title or draft.news_title,
            category=draft.category,
            brand_color=_get_brand_color(ctx, draft.category),
            output_dir=ctx.work_dir / "output" / "cards",
            dry_run=ctx.dry_run,
        )
        if card_path:
            _update_card_path(get_db, ctx, draft, card_path)

    _run_publish_stage(pass_args)

    print("\n=== 流程完成 ===")


def _run_publish_stage(pass_args: list[str]):
    print("\n=== 第4步: 渠道发布/草稿生成 ===")
    publisher = importlib.import_module("publish_channels")
    publisher.main(["--enabled", *pass_args])



def _get_brand_color(ctx, category: str) -> str:
    for source in ctx.config.get("sources", []):
        if source["category"] == category:
            return source.get("brand_color", "#333333")
    return "#333333"


def _update_card_path(get_db, ctx, draft, card_path: Path):
    with get_db(ctx.db_path) as conn:
        if draft.brief_id:
            conn.execute(
                "UPDATE post_drafts SET card_path=? WHERE brief_id=? AND status='pending'",
                (str(card_path), draft.brief_id),
            )
        else:
            conn.execute(
                "UPDATE post_drafts SET card_path=? WHERE news_url=? AND status='pending'",
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
