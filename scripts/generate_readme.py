#!/usr/bin/env python3
"""Auto-generate the Available Skills section in README.md from SKILL.md files."""

from __future__ import annotations

import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
START_MARKER = "<!-- SKILLS:START -->"
END_MARKER = "<!-- SKILLS:END -->"


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract name and description from YAML frontmatter."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = m.group(1)

    # name
    name_m = re.search(r"^name:\s*(.+)", fm, re.MULTILINE)
    name = name_m.group(1).strip() if name_m else ""

    # description: handle > (folded) and | (literal) block styles
    desc = ""
    block_m = re.search(r"^description:\s*([>|])\n((?:\s+.*\n)*)", fm, re.MULTILINE)
    if block_m:
        style, body = block_m.group(1), block_m.group(2)
        lines = [l.rstrip() for l in body.split("\n")]
        # dedent: remove common leading whitespace
        indent = min((len(l) - len(l.lstrip())) for l in lines if l.strip())
        lines = [l[indent:] if l.strip() else "" for l in lines]
        if style == ">":
            desc = " ".join(l for l in lines if l).strip()
        else:  # |
            desc = "\n".join(lines).strip()
    else:
        inline_m = re.search(r"^description:\s*(.+)", fm, re.MULTILINE)
        if inline_m:
            desc = inline_m.group(1).strip().strip('"').strip("'")

    return {"name": name, "description": desc}


def load_plugin_info(plugin_root: Path) -> dict[str, str]:
    """Load plugin name and description from plugin.json."""
    pj = plugin_root / ".claude-plugin" / "plugin.json"
    if not pj.exists():
        return {"name": plugin_root.name, "description": ""}
    with open(pj) as f:
        data = json.load(f)
    return {
        "name": data.get("name", plugin_root.name),
        "description": data.get("description", ""),
    }


def collect_skills() -> dict[str, dict]:
    """Scan all SKILL.md files and group by plugin."""
    plugins: dict[str, dict] = {}  # plugin_name -> {info, skills: [...]}

    patterns = [
        str(ROOT / "plugins" / "*" / "skills" / "*" / "SKILL.md"),
        str(ROOT / "plugins" / "*" / "*" / "skills" / "*" / "SKILL.md"),
    ]
    seen_paths: set[str] = set()

    for pattern in patterns:
        for skill_md in sorted(glob.glob(pattern)):
            if skill_md in seen_paths:
                continue
            seen_paths.add(skill_md)

            skill_path = Path(skill_md)
            # Determine plugin root
            parts = skill_path.relative_to(ROOT / "plugins").parts
            plugin_name = parts[0]
            plugin_root = ROOT / "plugins" / plugin_name

            # Skip internal xiaohongshu-skills (sub-module, not top-level plugins)
            if "xiaohongshu-skills/skills" in skill_md:
                continue

            if plugin_name not in plugins:
                plugins[plugin_name] = {
                    "info": load_plugin_info(plugin_root),
                    "skills": [],
                }

            with open(skill_md) as f:
                content = f.read()

            meta = parse_frontmatter(content)
            if not meta.get("name"):
                continue

            # First non-empty line after frontmatter as brief description fallback
            desc = meta["description"]
            if not desc:
                after_fm = content.split("---", 2)[-1].strip()
                first_line = after_fm.split("\n")[0].strip()
                if first_line and not first_line.startswith("#"):
                    desc = first_line

            plugins[plugin_name]["skills"].append({
                "name": meta["name"],
                "description": desc.split("\n")[0] if desc else "",  # first line only
                "path": str(skill_path.relative_to(ROOT)),
            })

    return plugins


def generate_markdown(plugins: dict[str, dict]) -> str:
    """Generate the skills catalog markdown."""
    lines: list[str] = []

    for plugin_name in sorted(plugins):
        p = plugins[plugin_name]
        display_name = p["info"]["name"]
        plugin_desc = p["info"]["description"]

        lines.append(f"### {display_name}")
        if plugin_desc:
            lines.append(f"> {plugin_desc}")
        lines.append("")

        lines.append("| Skill | Description |")
        lines.append("|-------|-------------|")

        for s in sorted(p["skills"], key=lambda x: x["name"]):
            name = s["name"]
            desc = s["description"]
            # Truncate long descriptions
            if len(desc) > 100:
                desc = desc[:97] + "..."
            # Escape pipe chars in description
            desc = desc.replace("|", "\\|")
            lines.append(f"| `/{name}` | {desc} |")

        lines.append("")

    return "\n".join(lines)


def update_readme(content: str) -> bool:
    """Replace content between markers in README.md. Returns True if changed."""
    readme = README_PATH.read_text(encoding="utf-8")

    if START_MARKER not in readme or END_MARKER not in readme:
        print(f"Warning: markers not found in {README_PATH}")
        return False

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    new_section = f"{START_MARKER}\n{content}\n{END_MARKER}"
    new_readme = pattern.sub(new_section, readme)

    if new_readme == readme:
        return False

    README_PATH.write_text(new_readme, encoding="utf-8")
    return True


def main() -> None:
    plugins = collect_skills()

    total_skills = sum(len(p["skills"]) for p in plugins.values())
    print(f"Found {total_skills} skills across {len(plugins)} plugins")

    md = generate_markdown(plugins)

    if update_readme(md):
        print(f"Updated {README_PATH}")
    else:
        print(f"No changes to {README_PATH}")


if __name__ == "__main__":
    main()
