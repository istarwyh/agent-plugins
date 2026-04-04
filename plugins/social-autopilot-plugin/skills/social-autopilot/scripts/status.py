import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from common import WORK_DIR, load_context, init_db, get_db


def main(args: list[str] = None):
    if args is None:
        args = []
    parser = argparse.ArgumentParser(description="运行状态检查")
    parser.parse_args(args)

    print("=" * 50)
    print("  Social Autopilot 状态")
    print("=" * 50)

    # 1. Work directory
    print(f"\n工作目录: {WORK_DIR}")
    print(f"  存在: {'✓' if WORK_DIR.exists() else '✗'}")

    env_path = WORK_DIR / ".env"
    print(f"  .env: {'✓' if env_path.exists() else '✗ (未配置)'}")

    config_path = WORK_DIR / "config.json"
    print(f"  config.json: {'✓' if config_path.exists() else '✗ (使用默认)'}")

    # 2. Database stats
    db_path = WORK_DIR / "data" / "news.db"
    if db_path.exists():
        try:
            with get_db(db_path) as conn:
                news_count = conn.execute("SELECT COUNT(*) FROM processed_news").fetchone()[0]
                draft_count = conn.execute("SELECT COUNT(*) FROM post_drafts").fetchone()[0]
                pending = conn.execute("SELECT COUNT(*) FROM post_drafts WHERE status='pending'").fetchone()[0]
                scheduled = conn.execute("SELECT COUNT(*) FROM post_drafts WHERE status='scheduled'").fetchone()[0]

                last_run = conn.execute(
                    "SELECT * FROM run_log ORDER BY run_at DESC LIMIT 1"
                ).fetchone()

            print(f"\n数据库:")
            print(f"  已处理新闻: {news_count}")
            print(f"  帖子草稿: {draft_count} (待发布: {pending}, 已排期: {scheduled})")

            if last_run:
                print(f"\n最近一次运行:")
                print(f"  时间: {last_run['run_at']}")
                print(f"  抓取: {last_run['news_fetched']}, 新增: {last_run['news_new']}")
                print(f"  生成帖子: {last_run['posts_created']}")
                errors = json.loads(last_run["errors"] or "[]")
                if errors:
                    print(f"  错误: {len(errors)} 个")
                    for e in errors[:3]:
                        print(f"    - {e}")
        except sqlite3.OperationalError:
            print("\n数据库: 表未初始化")
    else:
        print(f"\n数据库: 不存在 (首次运行时自动创建)")

    # 3. Output files
    news_dir = WORK_DIR / "output" / "news"
    drafts_dir = WORK_DIR / "output" / "drafts"
    cards_dir = WORK_DIR / "output" / "cards"

    news_files = list(news_dir.glob("news_*.json")) if news_dir.exists() else []
    draft_files = list(drafts_dir.glob("drafts_*.json")) if drafts_dir.exists() else []
    card_files = list(cards_dir.glob("card_*.png")) if cards_dir.exists() else []

    print(f"\n输出文件:")
    print(f"  新闻JSON: {len(news_files)} 个")
    print(f"  帖子草稿: {len(draft_files)} 个")
    print(f"  卡片图片: {len(card_files)} 个")

    # 4. API status
    print(f"\nAPI配置:")
    try:
        ctx = load_context(dry_run=True)
        print(f"  OpenAI Key: {'✓ 已配置' if ctx.openai_key else '✗ 未配置'}")
        print(f"  OpenAI Model: {ctx.openai_model}")
        print(f"  Meta Page ID: {'✓ 已配置' if ctx.meta_page_id else '✗ 未配置'}")
        print(f"  Meta Token: {'✓ 已配置' if ctx.meta_token else '✗ 未配置'}")
        print(f"  Instagram ID: {'✓ 已配置' if ctx.meta_ig_id else '✗ 未配置'}")
    except Exception:
        print("  ⚠ 无法加载配置")

    # 5. Cron status
    import subprocess
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        crontab = result.stdout if result.returncode == 0 else ""
        has_cron = "social-autopilot" in crontab
        print(f"\n定时任务: {'✓ 已安装' if has_cron else '✗ 未安装'}")
    except FileNotFoundError:
        print("\n定时任务: ⚠ crontab 不可用")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
