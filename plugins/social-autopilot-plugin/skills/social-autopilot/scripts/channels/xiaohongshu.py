import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common import SKILL_DIR, get_db
from channels.base import ChannelResult

INSTALL_HINT = """小红书渠道未检测到 xiaohongshu-plugin。
安装方式一：
  npx skills add istarwyh/agent-plugins

安装方式二：
  claude plugin marketplace add istarwyh/agent-plugins
  claude plugin install xiaohongshu-plugin@agent-plugins

安装后重启 Claude Code，并运行：
  /setup-xhs
  /xhs-login

如果你已手动安装小红书 CLI，可设置：
  XHS_CLI_PATH=/absolute/path/to/xiaohongshu-skills/scripts/cli.py"""


@dataclass
class XiaohongshuStatus:
    state: str
    cli_path: Path | None = None
    message: str = ""
    stdout: str = ""
    stderr: str = ""

    @property
    def available(self) -> bool:
        return self.cli_path is not None

    @property
    def logged_in(self) -> bool:
        return self.state == "logged_in"


def resolve_xhs_cli() -> Path | None:
    candidates: list[Path] = []
    env_path = os.getenv("XHS_CLI_PATH", "").strip()
    if env_path:
        candidates.append(Path(env_path).expanduser())

    candidates.append(
        SKILL_DIR.parents[2]
        / "xiaohongshu-plugin"
        / "xiaohongshu-skills"
        / "scripts"
        / "cli.py"
    )

    for path in candidates:
        if path.exists():
            return path
    return None


def check_login_status(check_login: bool = True, timeout: int = 30) -> XiaohongshuStatus:
    cli_path = resolve_xhs_cli()
    if not cli_path:
        return XiaohongshuStatus(state="missing", message=INSTALL_HINT)

    if not check_login:
        return XiaohongshuStatus(
            state="detected",
            cli_path=cli_path,
            message=f"已检测到小红书 CLI: {cli_path}",
        )

    try:
        result = subprocess.run(
            ["python3", str(cli_path), "check-login"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return XiaohongshuStatus(
            state="error",
            cli_path=cli_path,
            message="小红书登录检查超时，请运行 /setup-xhs 检查 Chrome Bridge。",
        )
    except OSError as exc:
        return XiaohongshuStatus(
            state="error",
            cli_path=cli_path,
            message=f"无法执行小红书 CLI: {exc}。请运行 /setup-xhs。",
        )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    parsed = _parse_json(stdout)
    logged_in = parsed.get("logged_in") if isinstance(parsed, dict) else None

    if result.returncode == 0 or logged_in is True:
        return XiaohongshuStatus(
            state="logged_in",
            cli_path=cli_path,
            message="小红书已登录。",
            stdout=stdout,
            stderr=stderr,
        )

    if result.returncode == 1 or logged_in is False:
        return XiaohongshuStatus(
            state="not_logged_in",
            cli_path=cli_path,
            message="小红书未登录，请运行 /xhs-login。",
            stdout=stdout,
            stderr=stderr,
        )

    detail = stderr or stdout or f"exit code {result.returncode}"
    return XiaohongshuStatus(
        state="error",
        cli_path=cli_path,
        message=f"小红书环境检查失败，请运行 /setup-xhs。详情: {detail[:300]}",
        stdout=stdout,
        stderr=stderr,
    )


def publish_pending(ctx, channel_config: dict[str, Any], dry_run: bool = False, limit: int = 10) -> ChannelResult:
    result = ChannelResult(channel="xiaohongshu")
    status = check_login_status(check_login=not dry_run)
    if status.state == "missing":
        result.skipped += 1
        result.add_message(status.message)
        return result

    if not dry_run and not status.logged_in:
        result.skipped += 1
        result.add_message(status.message)
        return result

    rows = _load_pending_rows(ctx.db_path, limit)
    if not rows:
        result.add_message("无待发布的小红书草稿。启用 channels.xiaohongshu 后重新生成帖子，或将草稿 platform 设为 xiaohongshu。")
        return result

    out_dir = ctx.work_dir / "output" / "xiaohongshu"
    out_dir.mkdir(parents=True, exist_ok=True)
    visibility = channel_config.get("visibility", "公开可见")
    config_tags = channel_config.get("tags", [])

    for row in rows:
        result.attempted += 1
        payload = _build_payload(row, config_tags, visibility, ctx.work_dir)
        if not payload["image_path"]:
            result.skipped += 1
            result.add_message(f"草稿 #{row['id']} 缺少可用图片，小红书图文笔记至少需要 1 张图片。")
            continue

        if dry_run:
            _print_preview(row["id"], payload)
            result.succeeded += 1
            continue

        title_file = out_dir / f"xhs_{row['id']}_{int(time.time())}_title.txt"
        content_file = out_dir / f"xhs_{row['id']}_{int(time.time())}_content.txt"
        title_file.write_text(payload["title"], encoding="utf-8")
        content_file.write_text(payload["content"], encoding="utf-8")

        cmd = [
            "python3",
            str(status.cli_path),
            "fill-publish",
            "--title-file",
            str(title_file),
            "--content-file",
            str(content_file),
            "--images",
            str(payload["image_path"]),
            "--visibility",
            visibility,
        ]
        if payload["tags"]:
            cmd.append("--tags")
            cmd.extend(payload["tags"])

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        except subprocess.TimeoutExpired:
            _update_row_status(ctx.db_path, row["id"], "failed")
            result.failed += 1
            result.add_message(f"草稿 #{row['id']} 小红书填表超时。")
            continue

        if proc.returncode == 0:
            _update_row_status(ctx.db_path, row["id"], "drafted")
            result.succeeded += 1
            result.add_message(f"草稿 #{row['id']} 已填入小红书发布页，未自动点击发布。")
        else:
            _update_row_status(ctx.db_path, row["id"], "failed")
            detail = (proc.stderr or proc.stdout or "unknown error").strip()[:300]
            result.failed += 1
            result.add_message(f"草稿 #{row['id']} 小红书填表失败: {detail}")

    return result


def _load_pending_rows(db_path: Path, limit: int):
    with get_db(db_path) as conn:
        return conn.execute(
            """
            SELECT * FROM post_drafts
            WHERE status = 'pending'
              AND lower(COALESCE(platform, '')) IN ('xiaohongshu', 'xhs', 'red')
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def _build_payload(row, config_tags: list[str], visibility: str, work_dir: Path) -> dict[str, Any]:
    platform_payload = _parse_json(_row_get(row, "platform_payload", "") or "")
    if not isinstance(platform_payload, dict):
        platform_payload = {}

    title_source = (
        platform_payload.get("title")
        or _row_get(row, "platform_title")
        or row["news_title"]
    )
    hashtags = _parse_hashtags(row["hashtags"])
    if _row_get(row, "platform_title") or platform_payload.get("title"):
        tags = _normalize_tags(hashtags)[:6]
    else:
        tags = _normalize_tags([*config_tags, *hashtags])[:8]

    image_path = _resolve_image(row["card_path"], work_dir)
    source = row["news_url"] or ""
    content_parts = [row["caption"].strip()]
    if source:
        content_parts.append(f"来源：{source}")

    return {
        "title": _truncate_xhs_title(str(title_source)),
        "content": "\n\n".join(part for part in content_parts if part),
        "tags": tags,
        "image_path": image_path,
        "visibility": visibility,
    }


def _row_get(row, key: str, default=None):
    try:
        return row[key]
    except (IndexError, KeyError):
        return default



def _parse_json(text: str) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _parse_hashtags(raw: str) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
        if isinstance(value, list):
            return [str(item) for item in value]
    except json.JSONDecodeError:
        pass
    return re.findall(r"#[\w一-鿿-]+", raw)


def _normalize_tags(tags: list[str]) -> list[str]:
    normalized = []
    seen = set()
    for tag in tags:
        tag = str(tag).strip()
        tag = tag.strip("#")
        tag = re.sub(r"\[话题\]#?$", "", tag)
        tag = re.sub(r"\s+", "", tag)
        if not tag:
            continue
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            normalized.append(tag)
    return normalized


def _resolve_image(card_path: str | None, work_dir: Path) -> Path | None:
    if not card_path:
        return None
    path = Path(card_path).expanduser()
    if not path.is_absolute():
        path = work_dir / path
    if path.exists():
        return path.resolve()
    return None


def _truncate_xhs_title(title: str, max_units: float = 20) -> str:
    text = re.sub(r"\s+", " ", title or "").strip() or "热点资讯更新"
    units = 0.0
    chars = []
    for char in text:
        cost = 0.5 if ord(char) < 128 else 1.0
        if units + cost > max_units:
            break
        chars.append(char)
        units += cost
    return "".join(chars).strip() or "热点资讯更新"


def _update_row_status(db_path: Path, row_id: int, status: str):
    with get_db(db_path) as conn:
        conn.execute(
            "UPDATE post_drafts SET status=?, scheduled_at=datetime('now') WHERE id=?",
            (status, row_id),
        )


def _print_preview(row_id: int, payload: dict[str, Any]):
    print(f"[DRY-RUN][xiaohongshu] 草稿 #{row_id}")
    print(f"  标题: {payload['title']}")
    print(f"  可见范围: {payload['visibility']}")
    print(f"  图片: {payload['image_path']}")
    print(f"  标签: {', '.join(payload['tags']) if payload['tags'] else '(无)'}")
    preview = payload["content"].replace("\n", " ")[:160]
    print(f"  正文预览: {preview}")
