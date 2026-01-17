<div align="center">

# 🤖 Gemini Plugin for Claude Code

**A comprehensive plugin for interacting with Google Gemini AI capabilities**

[![Gemini Plugin](https://img.shields.io/badge/Gemini-Plugin-blue?style=for-the-badge)](https://github.com/istarwyh/agent-plugins/tree/master/plugins/gemini-plugin)
[![Claude Code](https://img.shields.io/badge/Claude-Plugin-purple?style=for-the-badge)](https://claude.ai)

</div>

---

## ✨ Overview

**Gemini Plugin** is a powerful Claude Code plugin that provides seamless integration with Google Gemini's AI capabilities. It enables text generation, image creation, and intelligent conversations directly within your Claude Code environment.

**Key Features:**
- 🤖 **AI Text Generation**: Ask questions and get intelligent responses
- 🎨 **Image Generation**: Create images from text descriptions
- 🌐 **Multi-language Support**: Works with both English and Chinese interfaces
- 🔒 **Secure Authentication**: Persistent Google account integration
- 🔄 **Browser Automation**: Seamless interaction with Gemini web interface
- 📁 **Flexible Output**: Custom directories for generated content

---

## 📁 Plugin Structure

```
gemini-plugin/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata and configuration
├── skills/
│   └── gemini-skill/            # Main Gemini AI skill
│       ├── scripts/             # Automation scripts
│       │   ├── ask_gemini.py    # Text generation interface
│       │   ├── generate_image.py # Image generation interface
│       │   ├── auth_manager.py  # Authentication handling
│       │   ├── browser_utils.py # Browser automation utilities
│       │   └── run.py           # Environment wrapper script
│       ├── data/                # Local storage (auth, browser state)
│       ├── references/          # Extended documentation
│       ├── SKILL.md             # Complete skill documentation
│       ├── README.md            # Skill-specific README
│       └── requirements.txt     # Python dependencies
└── README.md                    # This file - Plugin overview
```

---

## 🚀 Quick Start

### Installation

```bash
# Navigate to your Claude plugins directory
cd ~/.claude/plugins

# Clone the agent-plugins repository
git clone https://github.com/istarwyh/agent-plugins.git

# Copy the gemini-plugin
cp -r agent-plugins/plugins/gemini-plugin ./gemini-plugin

# Clean up
rm -rf agent-plugins
```

### Setup

```bash
# Navigate to the gemini-skill directory
cd ~/.claude/plugins/gemini-plugin/skills/gemini-skill

# Authenticate with Google (browser will open)
python scripts/run.py auth_manager.py setup

# Check authentication status
python scripts/run.py auth_manager.py status
```

---

## 🛠️ Usage

### Text Generation

```bash
# Ask Gemini a question
python scripts/run.py ask_gemini.py --question "What is artificial intelligence?"

# Creative writing
python scripts/run.py ask_gemini.py --question "Write a poem about spring"

# Code generation
python scripts/run.py ask_gemini.py --question "Write a quicksort algorithm in Python"
```

### Image Generation

```bash
# Generate an image
python scripts/run.py generate_image.py --prompt "A cute robot playing guitar"

# Specify output directory
python scripts/run.py generate_image.py --prompt "Futuristic cityscape" --output ./my_images

# Generate art
python scripts/run.py generate_image.py --prompt "Abstract art with vibrant colors"
```

---

## 📖 Documentation

### Core Documentation
- **[SKILL.md](skills/gemini-skill/SKILL.md)** - Complete skill documentation with bilingual support
- **[API Reference](skills/gemini-skill/references/api_reference.md)** - Detailed script documentation
- **[Troubleshooting Guide](skills/gemini-skill/references/troubleshooting.md)** - Common issues and solutions

### Quick Reference
- **Authentication**: `python scripts/run.py auth_manager.py setup`
- **Text Query**: `python scripts/run.py ask_gemini.py --question "..."`
- **Image Generation**: `python scripts/run.py generate_image.py --prompt "..."`

---

## 🔧 Configuration

### Plugin Configuration
The plugin is configured through `.claude-plugin/plugin.json`:

```json
{
  "name": "gemini-plugin",
  "description": "Query Google NotebookLM for source-grounded answers from your documents. Includes Gemini integration, browser automation, and library management.",
  "version": "1.0.0",
  "author": {
    "name": "xiaohui",
    "email": "talk@xiaohui.cool"
  }
}
```

### Environment Variables
Optional environment variables in `skills/gemini-skill/.env`:

```env
HEADLESS=false           # Browser visibility
SHOW_BROWSER=false       # Default browser display
STEALTH_ENABLED=true     # Human-like behavior
TYPING_WPM_MIN=160       # Typing speed range
TYPING_WPM_MAX=240
PAGE_LOAD_TIMEOUT=30000  # Page load timeout (ms)
```

---

## 🎯 Features in Detail

### Text Generation (`ask_gemini.py`)
- **Multi-language Support**: Works with both English and Chinese interfaces
- **Smart Input Detection**: Multiple selector strategies for reliable input
- **Response Stability**: Intelligent detection of complete responses
- **Error Handling**: Comprehensive retry logic and timeout management
- **Debug Mode**: Browser visibility for troubleshooting

### Image Generation (`generate_image.py`)
- **Automatic Mode Detection**: Finds image generation interface automatically
- **High-Quality Downloads**: Uses download buttons for best image quality
- **Screenshot Fallback**: Reliable backup for image capture
- **Multiple Images**: Supports generating multiple images per prompt
- **Custom Output**: Flexible directory and filename options

### Authentication Management (`auth_manager.py`)
- **Persistent Sessions**: Maintains login state across uses
- **Secure Storage**: Protected authentication data
- **Easy Setup**: Browser-based authentication flow
- **Status Monitoring**: Real-time authentication status checks

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Always use `run.py` wrapper |
| Authentication fails | Browser must be visible for setup |
| Rate limit exceeded | Wait or switch Google account |
| Image generation fails | Try with `--debug` flag |
| No response | Check internet connection and auth status |

### Common Solutions

```bash
# Re-authenticate
python scripts/run.py auth_manager.py reauth

# Check status
python scripts/run.py auth_manager.py status

# Debug mode
python scripts/run.py ask_gemini.py --question "..." --show-browser
python scripts/run.py generate_image.py --prompt "..." --debug
```

---

## 🚀 Advanced Usage

### Custom Prompts
- **Be Specific**: Detailed prompts produce better results
- **Visual Details**: Include colors, styles, and composition for images
- **Context**: Provide background information for better responses
- **Language**: Use English or Chinese based on your preference

### Batch Operations
```bash
# Generate multiple images
for prompt in "cat" "dog" "bird"; do
  python scripts/run.py generate_image.py --prompt "A cute $prompt"
done

# Ask multiple questions
questions=("What is AI?" "Explain ML" "Future of tech")
for q in "${questions[@]}"; do
  python scripts/run.py ask_gemini.py --question "$q"
done
```

---

## 🔒 Security & Privacy

- **Local Storage**: All data stored locally in `~/.claude/`
- **Secure Auth**: Google authentication handled securely
- **No Data Sharing**: No data shared with third parties
- **Protected Files**: Sensitive data protected by `.gitignore`

---

## 🤝 Contributing

We welcome contributions! Please see the [main repository](https://github.com/istarwyh/agent-plugins) for guidelines.

### Development Setup
```bash
# Clone the repository
git clone https://github.com/istarwyh/agent-plugins.git

# Navigate to the plugin
cd agent-plugins/plugins/gemini-plugin

# Make changes and test
cd skills/gemini-skill
python scripts/run.py auth_manager.py status
```

---

## 📋 Requirements

- **Python 3.8+**
- **Google account** with Gemini access
- **Chromium browser** (auto-installed)
- **Internet connection**
- **Claude Code** environment

---

## 🔗 Links

- **[Agent Plugins Marketplace](https://github.com/istarwyh/agent-plugins)** - Main repository
- **[Gemini Plugin](https://github.com/istarwyh/agent-plugins/tree/master/plugins/gemini-plugin)** - Plugin directory
- **[Gemini Skill](skills/gemini-skill/)** - Core skill implementation
- **[Report Issues](https://github.com/istarwyh/agent-plugins/issues)** - Bug reports and feature requests

---

## 📄 License

This plugin is part of the Agent Plugins marketplace. Please see the main repository for licensing information.

---

<div align="center">

### 🤖 Start using Gemini AI in Claude Code today!

Built for the Claude Code community by [xiaohui](talk@xiaohui.cool)

[Documentation](skills/gemini-skill/SKILL.md) • [Report Issue](https://github.com/istarwyh/agent-plugins/issues) • [Contributing](https://github.com/istarwyh/agent-plugins/blob/master/CONTRIBUTING.md)

</div>
