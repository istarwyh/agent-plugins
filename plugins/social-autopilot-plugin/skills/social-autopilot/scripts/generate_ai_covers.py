import argparse
import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from common import ensure_dirs, get_db, init_db, load_context

DEFAULT_PROMPT_STYLE = """Create a premium vertical social-media cover image for a geek news post.
Style: cinematic editorial poster, high-end collectible/toy photography mood, dramatic lighting, clean composition, vivid but tasteful colors.
Do not include readable text, watermarks, official logos, actor likenesses, or trademarked character designs. Use symbolic objects, silhouettes, props, atmosphere, and abstract visual cues instead.
Leave enough negative space for an app title overlay if needed."""


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="用 Codex Image 生成高质量社交封面")
    parser.add_argument("--platform", default="xiaohongshu", choices=["xiaohongshu", "meta", "all"])
    parser.add_argument("--limit", type=int, default=3, help="本次最多生成几张 AI 封面")
    parser.add_argument("--size", default="1024x1536", choices=["1024x1024", "1024x1536", "1536x1024", "auto"])
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--force", action="store_true", help="已有 card_path 时仍重新生成")
    parser.add_argument("--dry-run", action="store_true", help="只打印提示词和目标路径，不调用 Codex")
    return parser.parse_args(args)


def main(args: list[str] = None):
    if args is None:
        args = []
    opts = parse_args(args)
    ctx = load_context(dry_run=opts.dry_run)
    init_db(ctx.db_path)
    ensure_dirs()

    rows = _load_rows(ctx.db_path, opts.platform, opts.limit, opts.force)
    if not rows:
        print("无需要生成 AI 封面的待发布草稿。")
        return []

    out_dir = ctx.work_dir / "output" / "ai-covers"
    out_dir.mkdir(parents=True, exist_ok=True)

    if opts.dry_run:
        _print_dry_run(rows, out_dir, opts)
        return []

    _ensure_codex_ready()

    generated = []
    for row in rows:
        output_path = _output_path(out_dir, row)
        if output_path.exists() and not opts.force:
            _update_card_path(ctx.db_path, row["id"], output_path)
            generated.append(output_path)
            print(f"草稿 #{row['id']} 已有关联 AI 封面: {output_path}")
            continue

        prompt = _build_prompt(row)
        print(f"草稿 #{row['id']} 正在生成 AI 封面: {row['platform_title'] or row['news_title']}")
        proc = subprocess.run(
            _codex_command(ctx.work_dir, out_dir, output_path.name, prompt, opts.size, opts.quality),
            capture_output=True,
            text=True,
            timeout=240,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "unknown error").strip()[:500]
            print(f"草稿 #{row['id']} AI 封面生成失败: {detail}")
            continue
        if not output_path.exists():
            print(f"草稿 #{row['id']} AI 封面生成失败: 未找到输出文件 {output_path}")
            continue

        _update_card_path(ctx.db_path, row["id"], output_path)
        generated.append(output_path)
        print(f"草稿 #{row['id']} AI 封面已生成: {output_path}")
        time.sleep(2)

    print(f"AI 封面生成完成: {len(generated)} 张")
    return generated


def _load_rows(db_path: Path, platform: str, limit: int, force: bool):
    where = ["status = 'pending'"]
    params: list[Any] = []
    if platform != "all":
        aliases = [platform]
        if platform == "xiaohongshu":
            aliases.extend(["xhs", "red"])
        where.append(f"lower(COALESCE(platform, '')) IN ({','.join('?' for _ in aliases)})")
        params.extend(aliases)
    if not force:
        where.append("(card_path IS NULL OR card_path = '')")
    params.append(limit)

    with get_db(db_path) as conn:
        return conn.execute(
            f"""
            SELECT * FROM post_drafts
            WHERE {' AND '.join(where)}
            ORDER BY relevance_score DESC, created_at ASC
            LIMIT ?
            """,
            params,
        ).fetchall()


def _print_dry_run(rows, out_dir: Path, opts: argparse.Namespace) -> None:
    print(f"[DRY-RUN] 将为 {len(rows)} 条草稿生成 AI 封面，输出目录: {out_dir}")
    print(f"[DRY-RUN] provider=codex-image, size={opts.size}, quality={opts.quality}")
    for row in rows:
        print(f"\n草稿 #{row['id']} -> {_output_path(out_dir, row)}")
        print(_build_prompt(row)[:1200])


def _ensure_codex_ready() -> None:
    if not shutil.which("codex"):
        raise RuntimeError("Codex CLI 未安装。请运行: npm install -g @openai/codex，然后运行 codex login。")
    result = subprocess.run(["codex", "login", "status"], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "not logged in").strip()
        raise RuntimeError(f"Codex 未登录或登录状态不可用。请运行 codex login 后重试。详情: {detail[:300]}")


def _codex_command(work_dir: Path, out_dir: Path, filename: str, prompt: str, size: str, quality: str) -> list[str]:
    instruction = f"""Perform these tasks:
1. Use the built-in image_gen tool to generate exactly one PNG image file.
2. Prompt: {prompt}
3. Size: {size}
4. Quality: {quality}
5. Copy the generated image to '{out_dir}' using filename '{filename}'.
6. Do not overwrite an existing file unless this filename is already the requested target.
7. Print the saved file path and byte size."""
    return [
        "codex",
        "exec",
        instruction,
        "-C",
        str(work_dir),
        "-s",
        "workspace-write",
        "-c",
        'model_reasoning_effort="medium"',
        "--skip-git-repo-check",
    ]


def _build_prompt(row) -> str:
    payload = _parse_json(row["platform_payload"] or "") or {}
    title = payload.get("title") or row["platform_title"] or row["news_title"] or "热点资讯"
    body = payload.get("body") or row["caption"] or ""
    tags = payload.get("tags") or _parse_hashtags(row["hashtags"] or "")
    image_direction = row["image_suggestion"] or ""
    summary = _compact_text(body, 360)
    tag_text = ", ".join(str(tag).strip("#") for tag in tags[:8] if str(tag).strip("#"))
    category_style = _category_style(row["category"])

    return f"""{DEFAULT_PROMPT_STYLE}

Post title: {title}
Category: {row['category']} ({category_style})
News angle: {summary}
Suggested visual direction: {image_direction or 'symbolic scene that matches the news angle'}
Tags/themes: {tag_text or 'geek news, collectibles, pop culture'}
Composition: vertical cover, strong central subject, clean background, cinematic depth, suitable as the first image of a Xiaohongshu or Instagram carousel.
Avoid: readable text, UI screenshots, logos, exact copyrighted costumes, realistic celebrity faces, clutter."""


def _category_style(category: str) -> str:
    styles = {
        "漫威影业": "red cinematic superhero energy, multiverse atmosphere, metallic collectible props",
        "DC影业": "blue noir comic-book atmosphere, heroic silhouettes, rain and city lights",
        "星球大战": "space opera mood, desert/space silhouettes, glowing sci-fi props",
        "F1 2026": "high-speed racing mood, carbon fiber, neon track lights, motion blur",
        "游戏": "next-gen gaming mood, stylized controller/console props, neon ambience",
    }
    return styles.get(category, "premium geek culture editorial style")


def _output_path(out_dir: Path, row) -> Path:
    slug = _safe_slug(row["platform_title"] or row["news_title"] or "cover")
    return out_dir / f"{row['platform']}_{row['id']}_{slug}.png"


def _update_card_path(db_path: Path, row_id: int, image_path: Path) -> None:
    with get_db(db_path) as conn:
        conn.execute("UPDATE post_drafts SET card_path=? WHERE id=?", (str(image_path), row_id))


def _parse_json(text: str) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
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


def _compact_text(text: str, max_chars: int) -> str:
    return re.sub(r"\s+", " ", text).strip()[:max_chars]


def _safe_slug(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    return (slug or "cover")[:48]


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
