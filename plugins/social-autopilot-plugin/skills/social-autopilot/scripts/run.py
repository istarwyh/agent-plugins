import importlib
import sys
from pathlib import Path

SCRIPTS = {
    "setup.py": "setup",
    "poll_news.py": "poll_news",
    "generate_posts.py": "generate_posts",
    "generate_card.py": "generate_card",
    "schedule_meta.py": "schedule_meta",
    "install_cron.py": "install_cron",
    "status.py": "status",
    "pipeline": "pipeline",
}


def run_pipeline(args: list[str]):
    """Run full pipeline: poll → generate posts → generate cards → schedule."""
    from common import load_context, init_db, ensure_dirs

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
        print("未生成帖子，流程结束。")
        return

    print(f"\n=== 第3步: 生成卡片图 ({len(drafts)} 条帖子) ===")
    card = importlib.import_module("generate_card")
    for draft in drafts:
        card.generate_single_card(
            title=draft.news_title,
            category=draft.category,
            brand_color=_get_brand_color(ctx, draft.category),
            output_dir=ctx.work_dir / "output" / "cards",
            dry_run=ctx.dry_run,
        )

    if ctx.meta_token and not ctx.dry_run:
        print(f"\n=== 第4步: Meta排期 ===")
        sched = importlib.import_module("schedule_meta")
        sched.main(pass_args)
    else:
        print("\n=== Meta排期已跳过（未配置Token或dry-run模式）===")

    print("\n=== 流程完成 ===")


def _get_brand_color(ctx, category: str) -> str:
    for source in ctx.config.get("sources", []):
        if source["category"] == category:
            return source.get("brand_color", "#333333")
    return "#333333"


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
