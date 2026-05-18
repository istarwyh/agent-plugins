import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from loguru import logger

from common import load_context, init_db, ensure_dirs, get_db

GRAPH_API = "https://graph.facebook.com/v19.0"
BRT = ZoneInfo("America/Sao_Paulo")
GOLDEN_HOURS = [9, 12, 17, 19, 21]


def calculate_publish_time(is_urgent: bool = False) -> datetime:
    now = datetime.now(BRT)
    if is_urgent:
        return now + timedelta(minutes=30)
    for hour in GOLDEN_HOURS:
        if hour > now.hour:
            target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if target - now > timedelta(minutes=15):
                return target
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=GOLDEN_HOURS[0], minute=0, second=0, microsecond=0)


def schedule_facebook(
    page_id: str, token: str, message: str, publish_time: datetime,
) -> str | None:
    min_time = datetime.now(BRT) + timedelta(minutes=10)
    if publish_time < min_time:
        publish_time = min_time

    try:
        resp = requests.post(
            f"{GRAPH_API}/{page_id}/feed",
            data={
                "message": message,
                "published": "false",
                "scheduled_publish_time": int(publish_time.timestamp()),
                "access_token": token,
            },
            timeout=30,
        )
        resp.raise_for_status()
        post_id = resp.json().get("id")
        logger.info(f"Facebook排期成功: {post_id} @ {publish_time}")
        return post_id
    except requests.RequestException as e:
        logger.error(f"Facebook排期失败: {e}")
        return None


def publish_instagram(
    ig_user_id: str, token: str, image_url: str, caption: str,
) -> str | None:
    if not ig_user_id:
        return None
    try:
        resp1 = requests.post(
            f"{GRAPH_API}/{ig_user_id}/media",
            data={"image_url": image_url, "caption": caption, "access_token": token},
            timeout=60,
        )
        resp1.raise_for_status()
        container_id = resp1.json()["id"]

        for _ in range(12):
            check = requests.get(
                f"{GRAPH_API}/{container_id}",
                params={"fields": "status_code", "access_token": token},
            )
            status = check.json().get("status_code")
            if status == "FINISHED":
                break
            if status == "ERROR":
                raise Exception(f"容器处理失败: {check.json()}")
            time.sleep(5)

        resp2 = requests.post(
            f"{GRAPH_API}/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
            timeout=30,
        )
        resp2.raise_for_status()
        media_id = resp2.json()["id"]
        logger.info(f"Instagram发布成功: {media_id}")
        return media_id
    except Exception as e:
        logger.error(f"Instagram发布失败: {e}")
        return None


def check_token(token: str) -> dict:
    try:
        resp = requests.get(
            f"{GRAPH_API}/debug_token",
            params={"input_token": token, "access_token": token},
        )
        data = resp.json().get("data", {})
        return {
            "valid": data.get("is_valid", False),
            "expires": data.get("expires_at", 0),
            "scopes": data.get("scopes", []),
        }
    except Exception:
        return {"valid": False, "expires": 0, "scopes": []}


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Meta排期发布")
    parser.add_argument("--mode", choices=["facebook_only", "instagram_only", "both"],
                        default="facebook_only")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(args)


def main(args: list[str] = None):
    if args is None:
        args = []
    opts = parse_args(args)
    ctx = load_context(dry_run=opts.dry_run)
    init_db(ctx.db_path)

    if not ctx.meta_token:
        print("META_PAGE_ACCESS_TOKEN 未配置，无法排期。请参考 SETUP_GUIDE.md 配置 Meta API。")
        return

    if opts.dry_run:
        info = check_token(ctx.meta_token)
        print(f"[DRY-RUN] Token状态: {'有效' if info['valid'] else '无效'}")
        print(f"[DRY-RUN] 权限: {', '.join(info['scopes'])}")
        return

    with get_db(ctx.db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM post_drafts
            WHERE status = 'pending'
              AND lower(COALESCE(platform, 'instagram')) IN ('instagram', 'meta', 'facebook')
            ORDER BY created_at ASC
            LIMIT 10
            """
        ).fetchall()

    if not rows:
        print("无待排期帖子")
        return

    scheduled = 0
    for row in rows:
        hashtags = json.loads(row["hashtags"])
        message = f"{row['caption']}\n\n{' '.join(hashtags)}"
        is_urgent = (row["relevance_score"] or 0) >= 0.85
        pub_time = calculate_publish_time(is_urgent=is_urgent)

        post_id = None
        if opts.mode in ("facebook_only", "both"):
            post_id = schedule_facebook(ctx.meta_page_id, ctx.meta_token, message, pub_time)

        if post_id:
            with get_db(ctx.db_path) as conn:
                conn.execute(
                    "UPDATE post_drafts SET status='scheduled', meta_post_id=?, scheduled_at=? WHERE id=?",
                    (post_id, pub_time.isoformat(), row["id"]),
                )
            scheduled += 1

    print(f"排期完成: {scheduled}/{len(rows)} 条帖子")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
