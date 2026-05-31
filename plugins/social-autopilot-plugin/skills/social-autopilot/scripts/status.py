import argparse
import json
import shutil
import sqlite3

from common import WORK_DIR, find_codex_image_skill, find_openai_image_skill, load_context, init_db, get_db
from channels.xiaohongshu import check_login_status


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
            init_db(db_path)
            with get_db(db_path) as conn:
                news_count = conn.execute("SELECT COUNT(*) FROM processed_news").fetchone()[0]
                brief_count = conn.execute("SELECT COUNT(*) FROM content_briefs").fetchone()[0]
                draft_count = conn.execute("SELECT COUNT(*) FROM post_drafts").fetchone()[0]
                pending = conn.execute("SELECT COUNT(*) FROM post_drafts WHERE status='pending'").fetchone()[0]
                scheduled = conn.execute("SELECT COUNT(*) FROM post_drafts WHERE status='scheduled'").fetchone()[0]
                platform_rows = conn.execute(
                    """
                    SELECT COALESCE(platform, 'instagram') AS platform, status, COUNT(*) AS count
                    FROM post_drafts
                    GROUP BY COALESCE(platform, 'instagram'), status
                    ORDER BY platform, status
                    """
                ).fetchall()

                last_run = conn.execute(
                    "SELECT * FROM run_log ORDER BY run_at DESC LIMIT 1"
                ).fetchone()

            print("\n数据库:")
            print(f"  已处理新闻: {news_count}")
            print(f"  内容简报: {brief_count}")
            print(f"  帖子草稿: {draft_count} (待发布: {pending}, 已排期: {scheduled})")
            if platform_rows:
                print("  按渠道/状态:")
                for row in platform_rows:
                    print(f"    - {row['platform']}/{row['status']}: {row['count']}")

            if last_run:
                print("\n最近一次运行:")
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
        print("\n数据库: 不存在 (首次运行时自动创建)")

    # 3. Output files
    news_dir = WORK_DIR / "output" / "news"
    drafts_dir = WORK_DIR / "output" / "drafts"
    cards_dir = WORK_DIR / "output" / "cards"

    news_files = list(news_dir.glob("news_*.json")) if news_dir.exists() else []
    draft_files = list(drafts_dir.glob("drafts_*.json")) if drafts_dir.exists() else []
    card_files = list(cards_dir.glob("card_*.png")) if cards_dir.exists() else []

    print("\n输出文件:")
    print(f"  新闻JSON: {len(news_files)} 个")
    print(f"  帖子草稿: {len(draft_files)} 个")
    print(f"  卡片图片: {len(card_files)} 个")

    # 4. API and channel status
    print("\nAPI与渠道配置:")
    try:
        ctx = load_context(dry_run=True)
        channels = ctx.config.get("channels", {})
        meta_cfg = channels.get("meta", {})
        xhs_cfg = channels.get("xiaohongshu", {})
        print(f"  OpenAI Key: {'✓ 已配置' if ctx.openai_key else '✗ 未配置'}")
        print(f"  OpenAI Model: {ctx.openai_model}")
        codex_image_skill_path = find_codex_image_skill()
        if codex_image_skill_path:
            codex_cli = shutil.which("codex")
            cli_state = f", Codex CLI: {codex_cli}" if codex_cli else ", Codex CLI: 未安装"
            print(f"  Codex Image Skill: ✓ 已检测 ({codex_image_skill_path}{cli_state})")
        else:
            print("  Codex Image Skill: ✗ 未安装")
        image_skill_path = find_openai_image_skill()
        if image_skill_path:
            print(f"  OpenAI Image Skill: ✓ 已检测 ({image_skill_path})")
        else:
            print("  OpenAI Image Skill: ✗ 未安装")
            print("    安装: npx skills add istarwyh/agent-plugins")
            print("    或: claude plugin install openai-plugin@agent-plugins")
        print(f"  Meta Enabled: {'✓ 是' if meta_cfg.get('enabled') else '✗ 否'}")
        print(f"  Meta Mode: {meta_cfg.get('mode', 'facebook_only')}")
        print(f"  Meta Page ID: {'✓ 已配置' if ctx.meta_page_id else '✗ 未配置'}")
        print(f"  Meta Token: {'✓ 已配置' if ctx.meta_token else '✗ 未配置'}")
        print(f"  Instagram ID: {'✓ 已配置' if ctx.meta_ig_id else '✗ 未配置'}")
        print(f"  Xiaohongshu Enabled: {'✓ 是' if xhs_cfg.get('enabled') else '✗ 否'}")
        print(f"  Xiaohongshu Publish Mode: {xhs_cfg.get('publish_mode', 'draft')}")
        print(f"  Xiaohongshu Visibility: {xhs_cfg.get('visibility', '公开可见')}")
        xhs_status = check_login_status(check_login=True, timeout=15)
        if xhs_status.state == "missing":
            print("  Xiaohongshu CLI: ✗ 未安装")
            print("    安装: npx skills add istarwyh/agent-plugins")
            print("    或: claude plugin install xiaohongshu-plugin@agent-plugins")
        elif xhs_status.state == "logged_in":
            print(f"  Xiaohongshu CLI: ✓ 已检测 ({xhs_status.cli_path})")
            print("  Xiaohongshu Login: ✓ 已登录")
        elif xhs_status.state == "not_logged_in":
            print(f"  Xiaohongshu CLI: ✓ 已检测 ({xhs_status.cli_path})")
            print("  Xiaohongshu Login: ✗ 未登录，请运行 /xhs-login")
        else:
            print(f"  Xiaohongshu CLI: ⚠ {xhs_status.message}")
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
