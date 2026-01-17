# NotebookLM & Gemini Skill API Reference

Complete API documentation for all NotebookLM and Gemini skill modules.

## Important: Always Use run.py Wrapper

**All commands must use the `run.py` wrapper to ensure proper environment:**

```bash
# ✅ CORRECT:
python scripts/run.py [script_name].py [arguments]

# ❌ WRONG:
python scripts/[script_name].py [arguments]  # Will fail without venv!
```

## Core Scripts

### ask_question.py
Query NotebookLM with automated browser interaction.

```bash
# Basic usage
python scripts/run.py ask_question.py --question "Your question"

# With specific notebook
python scripts/run.py ask_question.py --question "..." --notebook-id notebook-id

# With direct URL
python scripts/run.py ask_question.py --question "..." --notebook-url "https://..."

# Show browser (debugging)
python scripts/run.py ask_question.py --question "..." --show-browser
```

**Parameters:**
- `--question` (required): Question to ask
- `--notebook-id`: Use notebook from library
- `--notebook-url`: Use URL directly
- `--show-browser`: Make browser visible

**Returns:** Answer text with follow-up prompt appended

### ask_gemini.py
Query Gemini directly for general knowledge and AI assistance.

```bash
# Basic usage
python scripts/run.py ask_gemini.py --question "Your question"

# Show browser (debugging)
python scripts/run.py ask_gemini.py --question "..." --show-browser
```

**Parameters:**
- `--question` (required): Question to ask Gemini
- `--show-browser`: Make browser visible (useful for debugging)

**Returns:** Answer text from Gemini

**Use Cases:**
- General knowledge questions
- Creative writing and brainstorming
- Code generation and explanation
- Image generation queries
- Multi-modal questions
- Real-time information (if available)

**Differences from NotebookLM:**
- No notebook/document required
- Not limited to uploaded sources
- Broader knowledge base
- Can generate images and creative content
- Faster responses (no document context to load)

### generate_image.py
Generate images using Gemini's image generation capabilities.

```bash
# Basic usage
python scripts/run.py generate_image.py --prompt "Your image description"

# Specify output directory
python scripts/run.py generate_image.py --prompt "..." --output ./my_images

# Show browser (debugging)
python scripts/run.py generate_image.py --prompt "..." --show-browser
```

**Parameters:**
- `--prompt` (required): Image generation prompt/description
- `--output`: Output directory for images (default: current directory)
- `--show-browser`: Make browser visible (useful for debugging)

**Returns:** List of saved image paths

**How it works:**
1. Clicks the "Image" button to activate image generation mode
2. Submits the prompt
3. Waits for `generated-image` element to appear
4. Detects images from Google's CDN (`googleusercontent.com`)
5. Screenshots images directly from browser (most reliable)
6. Falls back to URL download if screenshot fails
7. Saves as PNG files with timestamps

**Features:**
- Precise image detection using `generated-image` selectors
- Screenshot-based saving (bypasses network issues)
- Automatic retry with URL download fallback
- Supports multiple images per generation
- Timestamped filenames prevent overwrites

**Example Output:**
```
generated_images/gemini_image_1_1767345225.png
generated_images/gemini_image_2_1767345225.png
```

**Examples:**
```bash
# Generate artwork
python scripts/run.py generate_image.py --prompt "A serene mountain landscape at sunset"

# Generate illustrations
python scripts/run.py generate_image.py --prompt "画一个可爱的雪人"

# Generate technical diagrams
python scripts/run.py generate_image.py --prompt "A flowchart showing the software development lifecycle"
```

### notebook_manager.py
Manage notebook library with CRUD operations.

```bash
# Smart Add (discover content first)
python scripts/run.py ask_question.py --question "What is the content of this notebook? What topics are covered? Provide a complete overview briefly and concisely" --notebook-url "[URL]"
# Then add with discovered info
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "Name" \
  --description "Description" \
  --topics "topic1,topic2"

# Direct add (when you know the content)
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "Name" \
  --description "What it contains" \
  --topics "topic1,topic2"

# List notebooks
python scripts/run.py notebook_manager.py list

# Search notebooks
python scripts/run.py notebook_manager.py search --query "keyword"

# Activate notebook
python scripts/run.py notebook_manager.py activate --id notebook-id

# Remove notebook
python scripts/run.py notebook_manager.py remove --id notebook-id

# Show statistics
python scripts/run.py notebook_manager.py stats
```

**Commands:**
- `add`: Add notebook (requires --url, --name, --topics)
- `list`: Show all notebooks
- `search`: Find notebooks by keyword
- `activate`: Set default notebook
- `remove`: Delete from library
- `stats`: Display library statistics

### auth_manager.py
Handle Google authentication and browser state.

```bash
# Setup (browser visible for login)
python scripts/run.py auth_manager.py setup

# Check status
python scripts/run.py auth_manager.py status

# Re-authenticate
python scripts/run.py auth_manager.py reauth

# Clear authentication
python scripts/run.py auth_manager.py clear
```

**Commands:**
- `setup`: Initial authentication (browser MUST be visible)
- `status`: Check if authenticated
- `reauth`: Clear and re-setup
- `clear`: Remove all auth data

### cleanup_manager.py
Clean skill data with preservation options.

```bash
# Preview cleanup
python scripts/run.py cleanup_manager.py

# Execute cleanup
python scripts/run.py cleanup_manager.py --confirm

# Keep library
python scripts/run.py cleanup_manager.py --confirm --preserve-library

# Force without prompt
python scripts/run.py cleanup_manager.py --confirm --force
```

**Options:**
- `--confirm`: Actually perform cleanup
- `--preserve-library`: Keep notebook library
- `--force`: Skip confirmation prompt

### run.py
Script wrapper that handles environment setup.

```bash
# Usage
python scripts/run.py [script_name].py [arguments]

# Examples
python scripts/run.py auth_manager.py status
python scripts/run.py ask_question.py --question "..."
```

**Automatic actions:**
1. Creates `.venv` if missing
2. Installs dependencies
3. Activates environment
4. Executes target script

## Python API Usage

### Using subprocess with run.py

```python
import subprocess
import json

# Query NotebookLM (with notebook)
result = subprocess.run([
    "python", "scripts/run.py", "ask_question.py",
    "--question", "Your question",
    "--notebook-id", "notebook-id"
], capture_output=True, text=True)

answer = result.stdout

# Query Gemini (no notebook required)
result = subprocess.run([
    "python", "scripts/run.py", "ask_gemini.py",
    "--question", "What is artificial intelligence?"
], capture_output=True, text=True)

answer = result.stdout
```

### Direct imports (after venv exists)

```python
# Only works if venv is already created and activated
from notebook_manager import NotebookLibrary
from auth_manager import AuthManager

library = NotebookLibrary()
notebooks = library.list_notebooks()

auth = AuthManager()
is_auth = auth.is_authenticated()
```

## Data Storage

Location: `~/.claude/skills/notebooklm/data/`

```
data/
├── library.json       # Notebook metadata
├── auth_info.json     # Auth status
└── browser_state/     # Browser cookies
    └── state.json
```

**Security:** Protected by `.gitignore`, never commit.

## Environment Variables

Optional `.env` file configuration:

```env
HEADLESS=false           # Browser visibility
SHOW_BROWSER=false       # Default display
STEALTH_ENABLED=true     # Human behavior
TYPING_WPM_MIN=160       # Typing speed
TYPING_WPM_MAX=240
DEFAULT_NOTEBOOK_ID=     # Default notebook
```

## Error Handling

Common patterns:

```python
# Using run.py prevents most errors
result = subprocess.run([
    "python", "scripts/run.py", "ask_question.py",
    "--question", "Question"
], capture_output=True, text=True)

if result.returncode != 0:
    error = result.stderr
    if "rate limit" in error.lower():
        # Wait or switch accounts
        pass
    elif "not authenticated" in error.lower():
        # Run auth setup
        subprocess.run(["python", "scripts/run.py", "auth_manager.py", "setup"])
```

## Rate Limits

Free Google accounts: 50 queries/day

Solutions:
1. Wait for reset (midnight PST)
2. Switch accounts with `reauth`
3. Use multiple Google accounts

## Advanced Patterns

### Parallel Queries

```python
import concurrent.futures
import subprocess

def query(question, notebook_id):
    result = subprocess.run([
        "python", "scripts/run.py", "ask_question.py",
        "--question", question,
        "--notebook-id", notebook_id
    ], capture_output=True, text=True)
    return result.stdout

# Run multiple queries simultaneously
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(query, q, nb)
        for q, nb in zip(questions, notebooks)
    ]
    results = [f.result() for f in futures]
```

### Batch Processing

```python
def batch_research(questions, notebook_id):
    results = []
    for question in questions:
        result = subprocess.run([
            "python", "scripts/run.py", "ask_question.py",
            "--question", question,
            "--notebook-id", notebook_id
        ], capture_output=True, text=True)
        results.append(result.stdout)
        time.sleep(2)  # Avoid rate limits
    return results
```

## Module Classes

### NotebookLibrary
- `add_notebook(url, name, topics)`
- `list_notebooks()`
- `search_notebooks(query)`
- `get_notebook(notebook_id)`
- `activate_notebook(notebook_id)`
- `remove_notebook(notebook_id)`

### AuthManager
- `is_authenticated()`
- `setup_auth(headless=False)`
- `get_auth_info()`
- `clear_auth()`
- `validate_auth()`

### BrowserSession (internal)
- Handles browser automation
- Manages stealth behavior
- Not intended for direct use

## Best Practices

1. **Always use run.py** - Ensures environment
2. **Check auth first** - Before operations
3. **Handle rate limits** - Implement retries
4. **Include context** - Questions are independent
5. **Clean sessions** - Use cleanup_manager