import argparse
import subprocess
import sys
from pathlib import Path

from common import WORK_DIR, SKILL_DIR


CRON_COMMENT = "# social-autopilot: geek news pipeline"
SCRIPTS_DIR = SKILL_DIR / "scripts"


def get_python_path() -> str:
    return sys.executable


def build_cron_line(python: str, priority: str, schedule: str) -> str:
    cmd = f"{python} {SCRIPTS_DIR / 'run.py'} poll_news.py --priority {priority}"
    log = WORK_DIR / "logs" / "pipeline.log"
    return f"{schedule} cd {WORK_DIR} && {cmd} >> {log} 2>&1"


def get_current_crontab() -> str:
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else ""
    except FileNotFoundError:
        return ""


def main(args: list[str] = None):
    if args is None:
        args = []
    parser = argparse.ArgumentParser(description="安装crontab定时任务")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--remove", action="store_true", help="移除已安装的定时任务")
    opts = parser.parse_args(args)

    python = get_python_path()
    current = get_current_crontab()

    if opts.remove:
        if CRON_COMMENT not in current:
            print("未找到已安装的定时任务")
            return
        lines = current.splitlines()
        cleaned = []
        skip_next = False
        for line in lines:
            if CRON_COMMENT in line:
                skip_next = True
                continue
            if skip_next:
                skip_next = False
                continue
            cleaned.append(line)
        new_crontab = "\n".join(cleaned) + "\n"
        if opts.dry_run:
            print("[DRY-RUN] 将移除以下定时任务")
        else:
            proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True)
            if proc.returncode == 0:
                print("✓ 定时任务已移除")
        return

    # Build new cron entries
    new_entries = [
        f"\n{CRON_COMMENT} (high priority: every 4 hours)",
        build_cron_line(python, "high", "0 */4 * * *"),
        f"{CRON_COMMENT} (medium priority: every 4 hours, offset 10min)",
        build_cron_line(python, "medium", "10 */4 * * *"),
        f"{CRON_COMMENT} (low priority: daily at 8am)",
        build_cron_line(python, "low", "0 8 * * *"),
    ]

    print("将安装以下定时任务:\n")
    for entry in new_entries:
        print(f"  {entry}")

    if opts.dry_run:
        print("\n[DRY-RUN] 未实际安装")
        return

    # Check for existing entries
    if CRON_COMMENT in current:
        print("\n⚠ 已存在定时任务，先移除旧任务...")
        main(["--remove"])
        current = get_current_crontab()

    new_crontab = current.rstrip("\n") + "\n" + "\n".join(new_entries) + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True)
    if proc.returncode == 0:
        print("\n✓ 定时任务已安装")
        print("验证: crontab -l")
    else:
        print("\n✗ 安装失败")


if __name__ == "__main__":
    main(sys.argv[1:])
