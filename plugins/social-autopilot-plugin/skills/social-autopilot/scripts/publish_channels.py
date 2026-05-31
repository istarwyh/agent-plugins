import argparse
import importlib

from common import get_enabled_channels, init_db, load_context
from channels import AVAILABLE_CHANNELS, ChannelResult
from channels.xiaohongshu import publish_pending as publish_xiaohongshu

CHANNEL_ALIASES = {
    "xhs": "xiaohongshu",
    "red": "xiaohongshu",
}


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="多渠道发布/草稿生成")
    parser.add_argument("--channel", choices=["meta", "xiaohongshu", "xhs", "red"])
    parser.add_argument("--all", action="store_true", help="运行所有已知渠道")
    parser.add_argument("--enabled", action="store_true", help="运行 config.json 中启用的渠道")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--xhs-publish-mode",
        choices=["draft", "publish"],
        help="覆盖小红书发布模式：draft=只填表，publish=直接发布",
    )
    return parser.parse_args(args)


def main(args: list[str] = None) -> list[ChannelResult]:
    if args is None:
        args = []
    opts = parse_args(args)
    ctx = load_context(dry_run=opts.dry_run)
    init_db(ctx.db_path)
    channels = _resolve_channels(opts, ctx.config)

    if not channels:
        print("没有启用的发布渠道。请在 ~/social-autopilot/config.json 的 channels 中启用。")
        return []

    results = []
    for channel in channels:
        if channel == "meta":
            results.append(_publish_meta(ctx, opts.dry_run))
        elif channel == "xiaohongshu":
            cfg = dict(ctx.config.get("channels", {}).get("xiaohongshu", {}))
            if opts.xhs_publish_mode:
                cfg["publish_mode"] = opts.xhs_publish_mode
            results.append(publish_xiaohongshu(ctx, cfg, dry_run=opts.dry_run, limit=opts.limit))
        else:
            result = ChannelResult(channel=channel, skipped=1)
            result.add_message(f"未知渠道: {channel}")
            results.append(result)

    print("\n=== 渠道发布汇总 ===")
    for result in results:
        result.print_summary()
    return results


def _resolve_channels(opts: argparse.Namespace, config: dict) -> list[str]:
    if opts.channel:
        return [_normalize_channel(opts.channel)]
    if opts.all:
        return list(AVAILABLE_CHANNELS)
    enabled = get_enabled_channels(config)
    if opts.enabled:
        return enabled
    return enabled


def _normalize_channel(channel: str) -> str:
    return CHANNEL_ALIASES.get(channel, channel)


def _publish_meta(ctx, dry_run: bool) -> ChannelResult:
    result = ChannelResult(channel="meta")
    cfg = ctx.config.get("channels", {}).get("meta", {})
    mode = cfg.get("mode", "facebook_only")

    if not ctx.meta_token:
        result.skipped += 1
        result.add_message("META_PAGE_ACCESS_TOKEN 未配置，跳过 Meta 渠道。")
        return result

    args = ["--mode", mode]
    if dry_run:
        args.append("--dry-run")

    schedule_meta = importlib.import_module("schedule_meta")
    schedule_meta.main(args)
    result.attempted += 1
    result.succeeded += 1
    result.add_message(f"已调用 Meta 渠道，mode={mode}。")
    return result


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
