import argparse
import re
import time
from pathlib import Path

from loguru import logger

from common import load_context, ensure_dirs, SKILL_DIR

TEMPLATE_PATH = SKILL_DIR / "templates" / "news_card.html"

CATEGORY_MAP = {
    "漫威影业": "MARVEL",
    "DC影业": "DC COMICS",
    "星球大战": "STAR WARS",
    "F1 2026": "FORMULA 1",
    "游戏": "GAMES",
}


def render_html(title: str, category: str, brand_color: str) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    display_cat = CATEGORY_MAP.get(category, category.upper())
    html = template.replace("{{TITLE}}", _escape_html(title))
    html = html.replace("{{CATEGORY}}", _escape_html(display_cat))
    html = html.replace("{{BRAND_COLOR}}", brand_color)
    return html


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _safe_filename(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    return slug[:60]


def generate_single_card(
    title: str,
    category: str,
    brand_color: str = "#333333",
    output_dir: Path = None,
    dry_run: bool = False,
) -> Path | None:
    if output_dir is None:
        output_dir = Path.home() / "social-autopilot" / "output" / "cards"
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d_%H%M%S")
    slug = _safe_filename(title)
    png_path = output_dir / f"card_{ts}_{slug}.png"

    if dry_run:
        print(f"[DRY-RUN] 将生成卡片: {png_path.name}")
        return None

    html = render_html(title, category, brand_color)

    # Write temp HTML
    tmp_html = output_dir / f"_tmp_{ts}.html"
    tmp_html.write_text(html, encoding="utf-8")

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1080})
            page.goto(f"file://{tmp_html.resolve()}")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(png_path), type="png")
            browser.close()

        logger.info(f"卡片已生成: {png_path}")
        return png_path
    except ImportError:
        logger.error("Playwright 未安装。运行: python -m playwright install chromium")
        return None
    except Exception as e:
        logger.error(f"卡片生成失败: {e}")
        return None
    finally:
        tmp_html.unlink(missing_ok=True)


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="新闻卡片图片生成")
    parser.add_argument("--title", required=True, help="新闻标题")
    parser.add_argument("--category", required=True, help="分类: marvel/dc/starwars/f1/games")
    parser.add_argument("--color", default="#333333", help="品牌色(十六进制)")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(args)


def main(args: list[str] = None):
    if args is None:
        args = []
    opts = parse_args(args)
    ctx = load_context(dry_run=opts.dry_run)
    ensure_dirs()

    # Resolve category and color
    category = opts.category
    color = opts.color
    for source in ctx.config.get("sources", []):
        if source["id"] == opts.category or source["category"] == opts.category:
            category = source["category"]
            color = source.get("brand_color", opts.color)
            break

    result = generate_single_card(
        title=opts.title,
        category=category,
        brand_color=color,
        output_dir=ctx.work_dir / "output" / "cards",
        dry_run=opts.dry_run,
    )
    if result:
        print(f"卡片图片: {result}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
