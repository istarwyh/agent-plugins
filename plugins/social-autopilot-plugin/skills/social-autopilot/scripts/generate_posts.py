import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

from openai import OpenAI
from loguru import logger

from common import load_context, init_db, ensure_dirs, get_db, get_enabled_channels
from models import ContentBrief, NewsItem, PostDraft

BRIEF_SYSTEM_PROMPT = """Você é um estrategista de conteúdo para um e-commerce geek.
Extraia apenas fatos presentes na notícia e transforme-os em um brief reutilizável para múltiplas plataformas.
Não escreva post final, não traduza para uma plataforma específica, não defina contagem de hashtags.
FORMATO: JSON estrito (sem markdown, sem code blocks)."""

META_SYSTEM_PROMPT = """Você é um especialista em marketing digital para um e-commerce brasileiro de colecionáveis geek.

PRODUTOS QUE VENDEMOS:
- Blocos de montar compatíveis com LEGO (super-heróis, Star Wars, veículos)
- Action figures e miniaturas (Marvel, DC, anime)
- Produtos temáticos (F1, games, cultura pop)

ESTILO META/INSTAGRAM:
- Português do Brasil informal mas profissional
- Entusiástico e autêntico, como um fã falando para outros fãs
- Usa gírias geek naturalmente (nerd, hype, épico, insano)
- Emoji relevantes (3-5 por post)
- Termina com CTA engajador

REGRAS:
- NUNCA inventar informações não presentes no brief
- SEMPRE vincular a notícia aos produtos quando possível
- Sem palavrões ou linguagem ofensiva
- Gere exatamente 20 hashtags

FORMATO: JSON estrito (sem markdown, sem code blocks)."""

XHS_SYSTEM_PROMPT = """你是小红书极客潮玩/影视资讯账号的内容编辑。
根据平台无关 brief 生成小红书原生图文笔记文案，不要翻译 Meta/Instagram 文案。

风格：
- 中文表达，自然像真实小红书资讯/种草笔记
- 标题有信息点和点击欲，但不夸大
- 正文分段清晰，适合图文笔记
- 可以轻度种草潮玩、积木、手办等商品关联，但不能编造新闻事实

规则：
- 标题最多 20 个中文字单位
- 正文只基于 brief 中的事实
- tags 生成 3-6 个，不带 #
- 不使用违禁夸大词

FORMATO: JSON estrito (sem markdown, sem code blocks)."""

PLATFORM_ALIASES = {
    "facebook": "meta",
    "instagram": "meta",
    "xhs": "xiaohongshu",
    "red": "xiaohongshu",
}


def fix_json(text: str) -> str:
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    text = re.sub(r"(?<=[\[,])\s*#", ' "#', text)
    return text


def build_brief_prompt(news: NewsItem, tags_seed: list[str]) -> str:
    return f"""NOTÍCIA:
Título: {news.title}
Categoria: {news.category}
Resumo: {news.summary}

TAGS/INTERESSES BASE: {', '.join(tags_seed)}

Responda EXCLUSIVAMENTE com JSON:
{{
  "relevance_score": <float 0-1>,
  "facts": ["3-6 fatos objetivos presentes na notícia"],
  "angle": "ângulo editorial reutilizável",
  "product_tie_in": "como conectar com colecionáveis geek sem inventar fatos",
  "image_direction": "direção visual reutilizável para card/capa",
  "base_tags": ["tags sem #, neutras e reutilizáveis"]
}}"""


def build_meta_prompt(brief: ContentBrief, tags_seed: list[str]) -> str:
    return f"""BRIEF:
Título original: {brief.news_title}
Categoria: {brief.category}
Fatos: {'; '.join(brief.facts)}
Ângulo: {brief.angle}
Conexão com produtos: {brief.product_tie_in}
Direção visual: {brief.image_direction}
Tags base: {', '.join([*brief.base_tags, *tags_seed])}

Responda EXCLUSIVAMENTE com JSON:
{{
  "caption": "texto até 150 palavras em PT-BR",
  "hashtags": ["#tag1", "... exatamente 20"],
  "cta": "call-to-action final"
}}"""


def build_xhs_prompt(brief: ContentBrief, channel_config: dict[str, Any]) -> str:
    configured_tags = channel_config.get("tags", [])
    return f"""内容简报：
原始标题：{brief.news_title}
分类：{brief.category}
事实：{'；'.join(brief.facts)}
内容角度：{brief.angle}
商品关联：{brief.product_tie_in}
视觉方向：{brief.image_direction}
基础标签：{', '.join([*brief.base_tags, *configured_tags])}

请输出小红书图文笔记 JSON：
{{
  "title": "20个中文字以内的小红书标题",
  "body": "中文正文，分段清晰，适合图文笔记",
  "tags": ["3-6个话题名，不带#"]
}}"""


def fix_hashtags(hashtags: list, tags_seed: list[str]) -> list[str]:
    fixed = []
    seen = set()
    for tag in hashtags:
        tag = str(tag).strip()
        if not tag:
            continue
        if not tag.startswith("#"):
            tag = f"#{tag}"
        low = tag.lower()
        if low not in seen:
            seen.add(low)
            fixed.append(tag)

    for seed in tags_seed:
        if len(fixed) >= 20:
            break
        seed = str(seed).strip()
        if not seed:
            continue
        if not seed.startswith("#"):
            seed = f"#{seed}"
        if seed.lower() not in seen:
            fixed.append(seed)
            seen.add(seed.lower())

    fallback = [
        "#colecionavel", "#geek", "#nerd", "#actionfigure",
        "#blocosdemontar", "#miniaturas", "#colecao", "#brasil",
        "#lojageek", "#presentegeek",
    ]
    for tag in fallback:
        if len(fixed) >= 20:
            break
        if tag not in seen:
            fixed.append(tag)
            seen.add(tag)

    return fixed[:20]


def generate_brief(
    client: OpenAI,
    model: str,
    news: NewsItem,
    tags_seed: list[str],
    min_relevance: float,
    max_retries: int = 3,
) -> ContentBrief | None:
    prompt = build_brief_prompt(news, tags_seed)
    for attempt in range(max_retries):
        try:
            data = _call_json(client, model, BRIEF_SYSTEM_PROMPT, prompt)
            relevance = float(data.get("relevance_score", 0))
            if relevance < min_relevance:
                logger.info(f"相关性不足 ({relevance:.2f}): {news.title[:50]}")
                return None
            return ContentBrief(
                news_url=news.url,
                news_title=news.title,
                category=news.category,
                source_id=news.source_id,
                relevance_score=relevance,
                facts=[str(item) for item in data.get("facts", [])][:6],
                angle=str(data.get("angle", "")),
                product_tie_in=str(data.get("product_tie_in", "")),
                image_direction=str(data.get("image_direction", "")),
                base_tags=_normalize_base_tags(data.get("base_tags", [])),
            )
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning(f"Brief生成失败 (尝试 {attempt + 1}): {exc}")
        except Exception as exc:
            logger.error(f"LLM调用错误: {exc}")
            break
    return None


def generate_platform_variant(
    client: OpenAI,
    model: str,
    brief: ContentBrief,
    platform: str,
    tags_seed: list[str],
    channel_config: dict[str, Any],
) -> PostDraft | None:
    normalized = PLATFORM_ALIASES.get(platform, platform)
    if normalized == "xiaohongshu":
        return generate_xhs_variant(client, model, brief, channel_config)
    return generate_meta_variant(client, model, brief, platform, tags_seed)


def generate_meta_variant(
    client: OpenAI,
    model: str,
    brief: ContentBrief,
    platform: str,
    tags_seed: list[str],
    max_retries: int = 3,
) -> PostDraft | None:
    prompt = build_meta_prompt(brief, tags_seed)
    for attempt in range(max_retries):
        try:
            data = _call_json(client, model, META_SYSTEM_PROMPT, prompt)
            hashtags = fix_hashtags(data.get("hashtags", []), [*brief.base_tags, *tags_seed])
            return PostDraft(
                brief_id=brief.id,
                news_url=brief.news_url,
                news_title=brief.news_title,
                category=brief.category,
                caption=str(data["caption"]),
                hashtags=hashtags,
                image_suggestion=brief.image_direction,
                cta=str(data.get("cta", "")),
                platform=platform,
                relevance_score=brief.relevance_score,
                platform_payload={"type": "meta", "raw": data},
            )
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning(f"Meta变体生成失败 (尝试 {attempt + 1}): {exc}")
        except Exception as exc:
            logger.error(f"LLM调用错误: {exc}")
            break
    return None


def generate_xhs_variant(
    client: OpenAI,
    model: str,
    brief: ContentBrief,
    channel_config: dict[str, Any],
    max_retries: int = 3,
) -> PostDraft | None:
    prompt = build_xhs_prompt(brief, channel_config)
    for attempt in range(max_retries):
        try:
            data = _call_json(client, model, XHS_SYSTEM_PROMPT, prompt)
            title = _truncate_xhs_title(str(data.get("title", brief.news_title)))
            body = str(data.get("body") or data.get("content") or "").strip()
            tags = _normalize_xhs_tags(data.get("tags", []), [*brief.base_tags, *channel_config.get("tags", [])])
            if not body:
                raise ValueError("XHS body is empty")
            return PostDraft(
                brief_id=brief.id,
                news_url=brief.news_url,
                news_title=brief.news_title,
                category=brief.category,
                caption=body,
                hashtags=tags,
                image_suggestion=brief.image_direction,
                cta="",
                platform="xiaohongshu",
                platform_title=title,
                relevance_score=brief.relevance_score,
                platform_payload={"type": "xiaohongshu", "title": title, "body": body, "tags": tags, "raw": data},
            )
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning(f"小红书变体生成失败 (尝试 {attempt + 1}): {exc}")
        except Exception as exc:
            logger.error(f"LLM调用错误: {exc}")
            break
    return None


def save_brief(brief: ContentBrief, db_path: Path) -> ContentBrief:
    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO content_briefs (
                news_url, news_title, category, source_id, relevance_score,
                facts, angle, product_tie_in, image_direction, base_tags
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(news_url) DO UPDATE SET
                news_title=excluded.news_title,
                category=excluded.category,
                source_id=excluded.source_id,
                relevance_score=excluded.relevance_score,
                facts=excluded.facts,
                angle=excluded.angle,
                product_tie_in=excluded.product_tie_in,
                image_direction=excluded.image_direction,
                base_tags=excluded.base_tags
            """,
            (
                brief.news_url,
                brief.news_title,
                brief.category,
                brief.source_id,
                brief.relevance_score,
                json.dumps(brief.facts, ensure_ascii=False),
                brief.angle,
                brief.product_tie_in,
                brief.image_direction,
                json.dumps(brief.base_tags, ensure_ascii=False),
            ),
        )
        row = conn.execute("SELECT * FROM content_briefs WHERE news_url=?", (brief.news_url,)).fetchone()
    return ContentBrief(
        id=row["id"],
        news_url=row["news_url"],
        news_title=row["news_title"],
        category=row["category"],
        source_id=row["source_id"] or "",
        relevance_score=row["relevance_score"] or 0,
        facts=json.loads(row["facts"] or "[]"),
        angle=row["angle"] or "",
        product_tie_in=row["product_tie_in"] or "",
        image_direction=row["image_direction"] or "",
        base_tags=json.loads(row["base_tags"] or "[]"),
    )


def save_draft(draft: PostDraft, db_path: Path) -> int:
    with get_db(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO post_drafts (
                brief_id, news_url, news_title, category, caption, hashtags,
                image_suggestion, cta, platform, platform_title, platform_payload,
                relevance_score
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                draft.brief_id,
                draft.news_url,
                draft.news_title,
                draft.category,
                draft.caption,
                json.dumps(draft.hashtags, ensure_ascii=False),
                draft.image_suggestion,
                draft.cta,
                draft.platform,
                draft.platform_title,
                json.dumps(draft.platform_payload or {}, ensure_ascii=False),
                draft.relevance_score,
            ),
        )
        return cursor.lastrowid


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LLM帖子生成")
    parser.add_argument("--input", help="指定新闻JSON文件路径")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(args)


def main(args: list[str] = None) -> list[PostDraft]:
    if args is None:
        args = []
    opts = parse_args(args)
    ctx = load_context(dry_run=opts.dry_run)
    init_db(ctx.db_path)
    ensure_dirs()

    news_file = Path(opts.input) if opts.input else _latest_news_file(ctx.work_dir)
    if not news_file:
        print("无待处理新闻文件")
        return []

    raw = json.loads(news_file.read_text())
    news_items = [NewsItem(**item) for item in raw][:ctx.max_posts]
    if not news_items:
        print("无待处理新闻")
        return []

    tags_map = {source["id"]: source.get("tags_seed", []) for source in ctx.config.get("sources", [])}
    platforms = get_enabled_channels(ctx.config) or ["meta"]

    if opts.dry_run:
        print(f"[DRY-RUN] 将处理 {len(news_items)} 条新闻，目标平台: {', '.join(platforms)}")
        return []

    if not ctx.openai_key:
        raise RuntimeError(f"缺少环境变量: OPENAI_API_KEY。请在 {ctx.work_dir / '.env'} 中填入对应值。")

    client_kwargs = {"api_key": ctx.openai_key}
    if ctx.openai_base_url:
        client_kwargs["base_url"] = ctx.openai_base_url
    client = OpenAI(**client_kwargs)

    drafts = []
    for item in news_items:
        tags_seed = tags_map.get(item.source_id, [])
        brief = generate_brief(client, ctx.openai_model, item, tags_seed, ctx.min_relevance)
        if not brief:
            continue
        brief = save_brief(brief, ctx.db_path)

        for platform in platforms:
            channel_config = ctx.config.get("channels", {}).get(platform, {})
            draft = generate_platform_variant(client, ctx.openai_model, brief, platform, tags_seed, channel_config)
            if not draft:
                continue
            save_draft(draft, ctx.db_path)
            drafts.append(draft)
            logger.info(f"生成: [{draft.platform}] [{draft.category}] {draft.caption[:60]}...")

    if drafts:
        out_dir = ctx.work_dir / "output" / "drafts"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_file = out_dir / f"drafts_{ts}.json"
        out_file.write_text(json.dumps(
            [draft.model_dump(mode="json") for draft in drafts],
            ensure_ascii=False, indent=2,
        ))

    print(f"帖子生成完成: {len(news_items)} 条新闻 → {len(drafts)} 条平台草稿")
    return drafts


def _call_json(client: OpenAI, model: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    resp = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        extra_body={"chat_template_kwargs": {"thinking": False}},
    )
    text = (resp.choices[0].message.content or "").strip()
    return json.loads(fix_json(text))


def _latest_news_file(work_dir: Path) -> Path | None:
    news_dir = work_dir / "output" / "news"
    files = sorted(news_dir.glob("news_*.json"), reverse=True)
    return files[0] if files else None


def _normalize_base_tags(tags: list[Any]) -> list[str]:
    return _dedupe_tags(str(tag).strip().strip("#") for tag in tags)[:10]


def _normalize_xhs_tags(tags: list[Any], fallback_tags: list[Any]) -> list[str]:
    normalized = _dedupe_tags(str(tag).strip().strip("#") for tag in tags)
    if len(normalized) < 3:
        normalized.extend(_dedupe_tags(str(tag).strip().strip("#") for tag in fallback_tags if str(tag).strip()))
    if len(normalized) < 3:
        normalized.extend(["极客资讯", "潮玩", "影视资讯"])
    return _dedupe_tags(normalized)[:6]


def _dedupe_tags(tags) -> list[str]:
    result = []
    seen = set()
    for tag in tags:
        tag = re.sub(r"\[话题\]#?$", "", str(tag))
        tag = re.sub(r"\s+", "", tag)
        if not tag:
            continue
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            result.append(tag)
    return result


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


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
