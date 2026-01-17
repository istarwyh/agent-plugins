---
name: template-skill
description: A template skill that demonstrates the structure and format for creating new Claude Skills.
---

# Template Skill

This is a template skill that demonstrates the recommended structure and format for creating new Claude Skills. Use this as a reference when building your own skills.

## When to Use This Skill

- When you need a starting point for creating a new skill
- When you want to understand the proper skill structure
- When you need examples of skill documentation

## What This Skill Does

This template provides:

1. **YAML Frontmatter** - Shows how to define skill metadata
2. **Structured Documentation** - Demonstrates clear organization
3. **Example Sections** - Includes all recommended sections
4. **Best Practices** - Shows formatting and content standards

## Instructions

When creating a new skill based on this template:

1. **Copy this template** to a new folder with your skill name (use lowercase-with-hyphens)
2. **Update the YAML frontmatter** with your skill's name and description
3. **Write clear instructions** for Claude on how to execute your skill
4. **Include examples** showing real-world usage
5. **Add any helper scripts** in a `scripts/` subdirectory
6. **Test thoroughly** across Claude.ai, Claude Code, or API

### Structure Guidelines

- Use clear headings (##, ###)
- Write instructions for Claude, not end users
- Include practical examples
- Document edge cases and error handling
- Add troubleshooting guidance

### Content Guidelines

- Be specific and actionable
- Use bullet points for lists
- Include code examples where relevant
- Show expected inputs and outputs
- Document any dependencies

## Examples

**User**: "Create a new skill for [specific task]"

**Claude's Process**:
1. Reads this template skill structure
2. Adapts the format to the specific use case
3. Fills in relevant sections with detailed instructions
4. Adds examples based on the task requirements
5. Ensures all necessary sections are included

**Output**:
```
skill-name/
├── SKILL.md          # Complete skill instructions
├── README.md         # Optional user documentation
└── scripts/          # Optional helper scripts
```

## Tips and Best Practices

- **Start simple** - Focus on one specific task
- **Be clear** - Write as if explaining to someone new
- **Include examples** - Real usage beats abstract descriptions
- **Test first** - Verify the skill works before publishing
- **Document dependencies** - Note any required tools or setup
- **Handle errors gracefully** - Explain what to do when things go wrong

## Common Use Cases

- Creating workflow automation skills
- Building documentation generation skills
- Developing code analysis skills
- Making file organization skills
- Implementing research and analysis skills

## Troubleshooting

- **Skill not loading**: Check YAML frontmatter syntax
- **Instructions unclear**: Add more specific examples
- **Doesn't work as expected**: Test with different inputs
- **Claude misunderstands**: Rephrase instructions more explicitly

## Additional Resources

- See [CONTRIBUTING.md](../CONTRIBUTING.md) for submission guidelines
- Review existing skills for real-world examples
- Check [Anthropic's official skills guide](https://support.claude.com/en/articles/12512198-creating-custom-skills)

---

**Remember**: Good skills are specific, well-documented, and tested. Start with this template and adapt it to your use case!
