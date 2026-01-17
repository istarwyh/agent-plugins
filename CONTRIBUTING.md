# Contributing to Agent Plugins

Thank you for your interest in contributing to Agent Plugins! This guide will help you add new skills that benefit the entire Claude community.

## Before You Start

- Ensure your skill is based on a **real use case**, not a hypothetical scenario
- Search existing skills to avoid duplicates
- If possible, attribute the use case to the original person or source
- Test your skill thoroughly before submitting

## Skill Requirements

All skills must:

1. **Solve a real problem** - Based on actual usage, not theoretical applications
2. **Be well-documented** - Include clear instructions, examples, and use cases
3. **Be accessible** - Written for non-technical users when possible
4. **Include examples** - Show practical, real-world usage
5. **Be tested** - Verify the skill works across Claude.ai, Claude Code, and/or API
6. **Be safe** - Confirm before destructive operations
7. **Be portable** - Work across Claude platforms when applicable

## Skill Structure

Create a new folder with your skill name (use lowercase and hyphens):

```
skill-name/
├── SKILL.md          # Required: Instructions for Claude with YAML frontmatter
├── README.md         # Optional but recommended: User-facing documentation
├── scripts/          # Optional: Helper scripts
├── templates/        # Optional: Document templates
└── resources/        # Optional: Reference files
```

## SKILL.md Template

Use this template for your skill:

```markdown
---
name: skill-name
description: One-sentence description of what this skill does and when to use it.
---

# Skill Name

Detailed description of the skill and what it helps users accomplish.

## When to Use This Skill

- Bullet point use case 1
- Bullet point use case 2
- Bullet point use case 3

## What This Skill Does

1. **Capability 1**: Description
2. **Capability 2**: Description
3. **Capability 3**: Description

## Instructions

[Detailed step-by-step instructions for Claude on how to execute this skill]

## Examples

**User**: "Example prompt"

**Claude's Process**:
1. Step 1
2. Step 2
3. Step 3

**Output**:
```
Show what the skill produces
```

## Tips and Best Practices

- Tip 1
- Tip 2
- Tip 3

## Common Use Cases

- Use case 1
- Use case 2
- Use case 3

## Troubleshooting

- Issue 1: Solution
- Issue 2: Solution
```

## Adding Your Skill to the Marketplace

### 1. Update marketplace.json

Add your skill to `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-skill-name",
  "description": "Brief description of what the skill does.",
  "source": "./your-skill-name",
  "category": "appropriate-category"
}
```

Available categories:
- `communication-writing` - Communication and writing tools
- `development` - Development and code tools
- `productivity-organization` - Productivity and organization tools
- `business-marketing` - Business and marketing tools
- `creative-media` - Creative and media tools
- `data-analysis` - Data analysis and processing tools
- `security-systems` - Security and system tools

### 2. Update README.md

Add your skill to the appropriate category section in the main README.md:

```markdown
- [**Your Skill Name**](./your-skill-name/) - Brief description of what it does and key features.
```

Follow the existing format:
- Use bold for skill names
- Keep descriptions concise (1-2 sentences)
- Link to the skill's directory
- Add attribution if based on someone's work

## Pull Request Process

1. Fork the repository
2. Create a branch: `git checkout -b add-skill-name`
3. Add your skill folder with all required files
4. Update `.claude-plugin/marketplace.json`
5. Update `README.md` in the appropriate category
6. Commit your changes: `git commit -m "Add [Skill Name] skill"`
7. Push to your fork: `git push origin add-skill-name`
8. Open a Pull Request

## Pull Request Guidelines

Your PR should include:

### Title
`Add [Skill Name] skill`

### Description
Explain the real-world use case and include:
- What problem it solves
- Who uses this workflow
- Attribution/inspiration source (if applicable)
- Example of how it's used
- Testing performed (platforms tested)

### Checklist
- [ ] SKILL.md with proper YAML frontmatter
- [ ] README.md (optional but recommended)
- [ ] marketplace.json updated
- [ ] Main README.md updated
- [ ] Tested on at least one Claude platform
- [ ] No duplicate functionality
- [ ] Safe operations (confirms before destructive actions)
- [ ] Clear documentation and examples

## Code of Conduct

- Be respectful and constructive
- Credit original sources and inspirations
- Focus on practical, helpful skills
- Write clear, accessible documentation
- Test your skills before submitting
- Help others in discussions and issues
- Report issues and bugs responsibly

## Attribution

When adding a skill based on someone's workflow or use case, include proper attribution:

```markdown
**Inspired by:** [Person Name]'s workflow
```

or

```markdown
**Credit:** Based on [Company/Team]'s process
```

or

```markdown
*By [@username](https://github.com/username)*
```

## Examples of Good Skills

- **Google Skill** - Shows browser automation, library management, and complex workflows
- See [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills) for more examples

## Testing Your Skill

Before submitting, test your skill:

### Claude Code Testing
```bash
# Copy skill to Claude skills directory
cp -r your-skill-name ~/.claude/skills/

# Start Claude Code
claude

# Test the skill
"What skills do I have?"
"[Use your skill with a test prompt]"
```

### Claude.ai Testing
1. Open claude.ai
2. Click the skills icon (🧩)
3. Upload your SKILL.md file
4. Test with example prompts

### API Testing
Use the Claude API with your skill to ensure it works programmatically.

## Need Help?

- Check the [template-skill](./template-skill/) for a reference implementation
- Review existing skills for examples
- Open an issue if you have questions
- Join discussions for community support

## Skill Categories Reference

### Communication & Writing
Skills for content creation, communication analysis, and writing assistance.

### Development & Code Tools
Skills for software development, testing, documentation, and technical workflows.

### Productivity & Organization
Skills for organizing files, managing tasks, and personal productivity.

### Business & Marketing
Skills for lead generation, competitive research, branding, and business development.

### Creative & Media
Skills for working with images, videos, audio, and creative content.

### Data & Analysis
Skills for data processing, analysis, and visualization.

### Security & Systems
Skills for security analysis, system administration, and forensics.

---

Thank you for contributing to Agent Plugins! Your contributions help the entire Claude community build better AI workflows.

## Questions?

Open an issue or start a discussion if you have questions about contributing or need help structuring your skill.
