import argparse
import json
import time
from pathlib import Path

from anthropic import Anthropic
from loguru import logger

from common import load_context, init_db, ensure_dirs, get_db
from models import NewsItem, PostDraft

SYSTEM_PROMPT = """Você é um especialista em marketing digital para um e-commerce brasileiro de colecionáveis geek.

PRODUTOS QUE VENDEMOS:
- Blocos de montar compatíveis com LEGO (super-heróis, Star Wars, veículos)
- Action figures e miniaturas (Marvel, DC, anime)
- Produtos temáticos (F1, games, cultura pop)

ESTILO DE ESCRITA:
- Entusiástico e autêntico, como um fã falando para outros fãs
- Usa gírias geek naturalmente (nerd, hype, épico, insano)
- Emoji relevantes (3-5 por post)
- Termina SEMPRE com um CTA engajador

REGRAS:
- NUNCA inventar informações não presentes na notícia
- SEMPRE vincular a notícia aos nossos produtos quando possível
- Português do Brasil informal mas profissional
- Sem palavrões ou linguagem ofensiva

FORMATO: JSON estrito (sem markdown, sem code blocks)"""


def build_prompt(news: NewsItem, tags_seed: list[str]) -> str:
    return f"""NOTÍCIA:
Título: {news.title}
Categoria: {news.category}
Resumo: {news.summary}

TAGS BASE: {', '.join(tags_seed)}

Responda EXCLUSIVAMENTE com JSON:
{{
  "relevance_score": <float 0-1>,
  "caption": "<texto até 150 palavras em PT-BR>",
  "hashtags": ["#tag1", ... exatamente 20],
  "image_suggestion": "<1 frase: qual imagem usar>",
  "cta": "<call-to-action final>"
}}"""


def fix_hashtags(hashtags: list, tags_seed: list[str]) -> list[str]:
    fixed = []
    seen = set()
    for tag in hashtags:
        tag = tag.strip()
        if not tag.startswith("#"):
            tag = f"#{tag}"
        low = tag.lower()
        if low not in seen:
            seen.add(low)
            fixed.append(tag)

    for seed in tags_seed:
        if len(fixed) >= 20:
            break
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


def generate_post(
    client: Anthropic,
    model: str,
    news: NewsItem,
    tags_seed: list[str],
    min_relevance: float,
    max_retries: int = 3,
) -> PostDraft | None:
    prompt = build_prompt(news, tags_seed)

    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=800,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]

            data = json.loads(text)

            relevance = float(data.get("relevance_score", 0))
            if relevance < min_relevance:
                logger.info(f"相关性不足 ({relevance:.2f}): {news.title[:50]}")
                return None

            hashtags = fix_hashtags(data.get("hashtags", []), tags_seed)

            return PostDraft(
                news_url=news.url,
                news_title=news.title,
                category=news.category,
                caption=data["caption"],
                hashtags=hashtags,
                image_suggestion=data.get("image_suggestion", ""),
                cta=data.get("cta", ""),
                relevance_score=relevance,
            )
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败 (尝试 {attempt+1}): {e}")
        except (ValueError, KeyError) as e:
            logger.warning(f"数据校验失败 (尝试 {attempt+1}): {e}")
        except Exception as e:
            logger.error(f"LLM调用错误: {e}")
            break

    return None


def save_draft(draft: PostDraft, db_path: Path):
    with get_db(db_path) as conn:
        conn.execute(
            "INSERT INTO post_drafts (news_url, news_title, category, caption, hashtags, "
            "image_suggestion, cta, relevance_score) VALUES (?,?,?,?,?,?,?,?)",
            (
                draft.news_url, draft.news_title, draft.category,
                draft.caption, json.dumps(draft.hashtags),
                draft.image_suggestion, draft.cta, draft.relevance_score,
            ),
        )


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

    # Load news items
    if opts.input:
        news_file = Path(opts.input)
    else:
        news_dir = ctx.work_dir / "output" / "news"
        files = sorted(news_dir.glob("news_*.json"), reverse=True)
        if not files:
            print("无待处理新闻文件")
            return []
        news_file = files[0]

    raw = json.loads(news_file.read_text())
    news_items = [NewsItem(**item) for item in raw]
    news_items = news_items[:ctx.max_posts]

    if not news_items:
        print("无待处理新闻")
        return []

    # Build tags map
    tags_map = {s["id"]: s.get("tags_seed", []) for s in ctx.config.get("sources", [])}

    if opts.dry_run:
        print(f"[DRY-RUN] 将处理 {len(news_items)} 条新闻")
        return []

    client = Anthropic(api_key=ctx.anthropic_key)
    drafts = []
    for item in news_items:
        draft = generate_post(
            client, ctx.anthropic_model, item,
            tags_map.get(item.source_id, []),
            ctx.min_relevance,
        )
        if draft:
            save_draft(draft, ctx.db_path)
            drafts.append(draft)
            logger.info(f"生成: [{draft.category}] {draft.caption[:60]}...")

    # Save drafts JSON
    if drafts:
        out_dir = ctx.work_dir / "output" / "drafts"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_file = out_dir / f"drafts_{ts}.json"
        out_file.write_text(json.dumps(
            [d.model_dump(mode="json") for d in drafts],
            ensure_ascii=False, indent=2,
        ))

    print(f"帖子生成完成: {len(news_items)} 条新闻 → {len(drafts)} 条帖子")
    return drafts


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
