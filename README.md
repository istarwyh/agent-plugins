# Agent Plugins

A curated collection of Claude Code skills and agent plugins for enhanced AI workflows and productivity.

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skills-purple.svg)](https://www.anthropic.com/news/skills)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Transform your Claude Code experience** with specialized skills that extend Claude's capabilities with domain-specific knowledge, workflows, and integrations.

---

## Contents

- [What Are Claude Skills?](#what-are-claude-skills)
- [Available Skills](#available-skills)
  - [Communication & Writing](#communication--writing)
  - [Development & Code Tools](#development--code-tools)
  - [Productivity & Organization](#productivity--organization)
- [Getting Started](#getting-started)
- [Creating Skills](#creating-skills)
- [Contributing](#contributing)
- [Resources](#resources)

## What Are Claude Skills?

Claude Skills are customizable workflows that teach Claude how to perform specific tasks according to your unique requirements. Skills enable Claude to execute tasks in a repeatable, standardized manner across all Claude platforms (Claude.ai, Claude Code, and API).

Each skill is a self-contained folder with instructions, scripts, and resources that Claude can invoke to accomplish specialized tasks.

## Available Skills

### Communication & Writing

- [**Google Skill (NotebookLM)**](./google-skill/) - Query Google NotebookLM notebooks directly from Claude Code for source-grounded, citation-backed answers from Gemini. Features browser automation, library management, and Gemini image generation. Reduces hallucinations by answering exclusively from your uploaded documents.

### Development & Code Tools

*Coming soon - add your skills here!*

### Productivity & Organization

*Coming soon - add your skills here!*

---

## Getting Started

### Installing Skills

#### Option 1: Clone the Entire Marketplace

```bash
# Clone this repository
git clone https://github.com/istarwyh/agent-plugins.git

# Copy specific skills to your Claude skills directory
mkdir -p ~/.claude/skills
cp -r agent-plugins/google-skill ~/.claude/skills/
```

#### Option 2: Install Individual Skills

```bash
# Navigate to your Claude skills directory
cd ~/.claude/skills

# Clone a specific skill
git clone https://github.com/istarwyh/agent-plugins.git temp-repo
mv temp-repo/google-skill ./google-skill
rm -rf temp-repo
```

### Using Skills in Claude Code

1. Place skills in `~/.claude/skills/` directory
2. Start Claude Code: `claude`
3. Skills load automatically and activate when relevant
4. Check available skills: "What skills do I have?"

### Using Skills in Claude.ai

1. Click the skill icon (🧩) in your chat interface
2. Upload the skill's SKILL.md file
3. Claude automatically activates the skill based on your task

### Using Skills via API

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    skills=["skill-id-here"],
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

See the [Skills API documentation](https://docs.claude.com/en/api/skills-guide) for details.

---

## Creating Skills

### Basic Skill Structure

Each skill is a folder containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: Skill instructions and metadata
├── scripts/          # Optional: Helper scripts
├── templates/        # Optional: Document templates
├── resources/        # Optional: Reference files
└── README.md         # Optional: User-facing documentation
```

### Minimal SKILL.md Template

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it.
---

# My Skill Name

Detailed description of the skill's purpose and capabilities.

## When to Use This Skill

- Use case 1
- Use case 2
- Use case 3

## Instructions

[Detailed instructions for Claude on how to execute this skill]

## Examples

[Real-world examples showing the skill in action]
```

### Skill Best Practices

- Focus on specific, repeatable tasks
- Include clear examples and edge cases
- Write instructions for Claude, not end users
- Test across Claude.ai, Claude Code, and API when possible
- Document prerequisites and dependencies
- Include error handling guidance

For detailed guidance, see our [template-skill](./template-skill/) example.

---

## Contributing

We welcome contributions! Whether you have a skill to share or want to improve existing ones, please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- How to submit new skills
- Skill quality standards
- Pull request process
- Code of conduct

### Quick Contribution Steps

1. Ensure your skill is based on a real use case
2. Check for duplicates in existing skills
3. Follow the skill structure template
4. Test your skill across platforms
5. Submit a pull request with clear documentation

---

## Resources

### Official Documentation

- [Claude Skills Overview](https://www.anthropic.com/news/skills) - Official announcement and features
- [Skills User Guide](https://support.claude.com/en/articles/12512180-using-skills-in-claude) - How to use skills in Claude
- [Creating Custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills) - Skill development guide
- [Skills API Documentation](https://docs.claude.com/en/api/skills-guide) - API integration guide

### Community Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official example skills
- [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills) - Community skill collection
- [Claude Community](https://community.anthropic.com) - Discuss skills with other users

### Inspiration

- [Lenny's Newsletter](https://www.lennysnewsletter.com/p/everyone-should-be-using-claude-code) - 50 ways people use Claude Code
- [Skills Marketplace](https://claude.ai/marketplace) - Discover and share skills

---

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Individual skills may have different licenses - please check each skill's folder for specific licensing information.

---

## Support

- Issues: [GitHub Issues](https://github.com/istarwyh/agent-plugins/issues)
- Discussions: [GitHub Discussions](https://github.com/istarwyh/agent-plugins/discussions)

---

**Note**: Claude Skills work across Claude.ai, Claude Code, and the Claude API. Once you create a skill, it's portable across all platforms, making your workflows consistent everywhere you use Claude.
