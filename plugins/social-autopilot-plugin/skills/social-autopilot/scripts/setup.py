import argparse
import json
import shutil
from pathlib import Path

from common import WORK_DIR, SKILL_DIR, DEFAULT_CONFIG, ensure_dirs, load_context
from channels.xiaohongshu import check_login_status

ENV_EXAMPLE = SKILL_DIR / ".env.example"


def main(args: list[str] = None):
    if args is None:
        args = []
    parser = argparse.ArgumentParser(description="首次配置向导")
    parser.add_argument("--dry-run", action="store_true")
    opts = parser.parse_args(args)

    print("=" * 50)
    print("  Social Autopilot 配置向导")
    print("=" * 50)

    # 1. Create work directory
    print(f"\n[1/5] 创建工作目录: {WORK_DIR}")
    if opts.dry_run:
        print("  [DRY-RUN] 跳过")
    else:
        ensure_dirs()
        print("  ✓ 目录已创建")

    # 2. Create .env
    env_path = WORK_DIR / ".env"
    print(f"\n[2/5] 配置文件: {env_path}")
    if env_path.exists():
        print("  ✓ .env 已存在，跳过")
    elif opts.dry_run:
        print("  [DRY-RUN] 跳过")
    else:
        shutil.copy2(ENV_EXAMPLE, env_path)
        print(f"  ✓ 已复制 .env.example → {env_path}")
        print("  ⚠ 请编辑此文件填入 OPENAI_API_KEY")

    # 3. Create config.json
    config_path = WORK_DIR / "config.json"
    print(f"\n[3/5] RSS源配置: {config_path}")
    if config_path.exists():
        print("  ✓ config.json 已存在，跳过")
    elif opts.dry_run:
        print("  [DRY-RUN] 跳过")
    else:
        config_path.write_text(
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2)
        )
        print("  ✓ 已写入默认配置（漫威/DC/星战/F1/游戏）")

    # 4. Check dependencies
    print("\n[4/5] 检查依赖")
    missing = []
    for pkg in ["feedparser", "openai", "pydantic", "dotenv", "loguru"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        missing.append("playwright")

    if missing:
        print(f"  ⚠ 缺少依赖: {', '.join(missing)}")
        req_path = SKILL_DIR / "requirements.txt"
        print(f"  运行: python -m pip install -r {req_path}")
        print("  然后: python -m playwright install chromium")
    else:
        print("  ✓ 所有依赖已安装")

    # 5. Check channels
    print("\n[5/5] 检查发布渠道")
    ctx = load_context(dry_run=True)
    print(f"  Meta: {'✓ 已配置 Token' if ctx.meta_token else '✗ 未配置 Token'}")
    xhs_status = check_login_status(check_login=not opts.dry_run)
    if xhs_status.state == "missing":
        print("  Xiaohongshu: ✗ 未安装")
        for line in xhs_status.message.splitlines():
            print(f"    {line}")
    elif xhs_status.state == "logged_in":
        print("  Xiaohongshu: ✓ 已安装且已登录")
    elif xhs_status.state == "detected":
        print(f"  Xiaohongshu: ✓ 已检测到 CLI ({xhs_status.cli_path})")
        print("    运行 /setup-xhs 和 /xhs-login 完成首次配置")
    else:
        print(f"  Xiaohongshu: ⚠ {xhs_status.message}")

    # Summary
    print("\n" + "=" * 50)
    print("配置完成! 下一步:")
    print(f"  1. 编辑 {env_path} 填入 API Key")
    print(f"  2. 运行测试: python scripts/run.py pipeline --dry-run")
    print(f"  3. 正式运行: python scripts/run.py pipeline")
    print("=" * 50)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
