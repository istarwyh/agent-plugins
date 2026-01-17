# NotebookLM Skill 优化建议

生成时间: 2026-01-02

## 🔴 高优先级 - 必须修复

### 1. 跨平台兼容性问题

**位置**: `scripts/browser_utils.py:31`

**问题**: 硬编码 macOS Chrome 路径，不支持 Windows/Linux

**当前代码**:
```python
executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
```

**建议修复**:
```python
import platform
import shutil

def get_chrome_path():
    """Get Chrome executable path for current platform"""
    system = platform.system()

    if system == "Darwin":  # macOS
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == "Windows":
        # Try common Windows paths
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    elif system == "Linux":
        # Try to find chrome in PATH
        chrome_cmd = shutil.which("google-chrome") or shutil.which("chrome")
        if chrome_cmd:
            return chrome_cmd

    return None  # Use default Chromium

# 使用:
chrome_path = get_chrome_path()
context = playwright.chromium.launch_persistent_context(
    user_data_dir=user_data_dir,
    executable_path=chrome_path,  # None will use default Chromium
    headless=headless,
    ...
)
```

---

### 2. JavaScript 注入安全问题

**位置**: `scripts/ask_gemini.py:156`

**问题**: f-string 注入导致 JavaScript 代码执行失败

**当前代码**:
```python
page.evaluate(f"""
    document.querySelector('{working_selector}').value = `{question}`;
""")
```

**问题**:
- `question` 中的特殊字符（引号、反引号）会破坏 JavaScript 语法
- 已在 `generate_image.py` 中修复，但 `ask_gemini.py` 仍存在

**建议修复**:
```python
# 使用参数传递，不要 f-string 拼接
page.evaluate("""
    (selector, text) => {
        const elem = document.querySelector(selector);
        if (elem) elem.value = text;
    }
""", working_selector, question)
```

---

### 3. .gitignore 不完整

**问题**: 测试目录和生成的图片未被忽略，会污染仓库

**当前状态** (git status):
```
?? final_intro/
?? generated_images/
?? skill_intro/
?? skill_intro_hq/
?? test_download/
?? test_typing/
```

**建议添加到 .gitignore**:
```gitignore
# Test artifacts and generated content
test_*/
*_test/
generated_images/
skill_intro*/
final_intro/

# Generated images
*.png
*.jpg
*.jpeg
!images/*.png  # Keep documentation images
```

---

## 🟡 中优先级 - 建议优化

### 4. 代码重复

**位置**: `ask_question.py` 和 `ask_gemini.py`

**问题**: 两个文件有 ~60% 的代码重复

**建议**: 创建 `common/response_handler.py`:
```python
def wait_for_response(page, selectors, timeout=120, thinking_selector=None):
    """通用的响应等待逻辑"""
    answer = None
    stable_count = 0
    last_text = None
    deadline = time.time() + timeout

    while time.time() < deadline:
        # Check thinking indicator
        if thinking_selector:
            try:
                thinking = page.query_selector(thinking_selector)
                if thinking and thinking.is_visible():
                    time.sleep(1)
                    continue
            except:
                pass

        # ... 提取公共逻辑

    return answer
```

---

### 5. 错误处理不完整

**多处位置**: 几乎所有脚本

**问题**:
```python
except Exception as e:
    print(f"❌ Error: {e}")  # 只打印，不抛出或记录
    return None
```

**建议**:
```python
import logging

logger = logging.getLogger(__name__)

try:
    # ...
except SpecificException as e:
    logger.error(f"Failed to ...: {e}", exc_info=True)
    raise  # 或者处理后返回
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

---

### 6. 超时配置硬编码

**位置**: 多处

**问题**:
```python
timeout=60000,  # 硬编码超时
timeout=10000,
```

**建议**: 统一到 `config.py`:
```python
# Timeouts (milliseconds)
DEFAULT_SELECTOR_TIMEOUT = 10000
LONG_SELECTOR_TIMEOUT = 60000
RESPONSE_TIMEOUT = 120000
IMAGE_GENERATION_TIMEOUT = 300000
```

---

### 7. 依赖版本过时

**文件**: `requirements.txt`

**当前**:
```
patchright==1.55.2
requests==2.31.0
python-dotenv==1.0.0
```

**建议**:
```
# 固定主版本，允许安全更新
patchright>=1.55.2,<2.0.0
requests>=2.31.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0

# 开发依赖（可选）
# pytest>=7.4.0
# black>=23.0.0
# ruff>=0.1.0
```

---

## 🟢 低优先级 - 可选增强

### 8. 缺少测试

**建议结构**:
```
tests/
├── __init__.py
├── conftest.py
├── test_auth.py
├── test_notebook_manager.py
├── test_browser_utils.py
└── fixtures/
    └── mock_responses.json
```

**示例测试**:
```python
# tests/test_notebook_manager.py
import pytest
from scripts.notebook_manager import NotebookLibrary

def test_add_notebook(tmp_path):
    lib = NotebookLibrary()
    notebook = lib.add_notebook(
        url="https://notebooklm.google.com/notebook/test",
        name="Test Notebook",
        description="Test description",
        topics=["test", "example"]
    )
    assert notebook['name'] == "Test Notebook"
    assert notebook['id'] == "test-notebook"
```

---

### 9. 日志系统

**建议**: 添加统一的日志配置

```python
# scripts/logger.py
import logging
import sys
from pathlib import Path

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Optional: file handler
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "skill.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
```

---

### 10. 环境变量配置

**建议**: 创建 `.env.example`:
```env
# Browser Configuration
HEADLESS=false
SHOW_BROWSER=false
STEALTH_ENABLED=true

# Typing Speed (words per minute)
TYPING_WPM_MIN=320
TYPING_WPM_MAX=480

# Timeouts (seconds)
PAGE_LOAD_TIMEOUT=300
QUERY_TIMEOUT=120
IMAGE_GENERATION_TIMEOUT=300

# Default Notebook
DEFAULT_NOTEBOOK_ID=

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
```

---

### 11. 性能优化

#### a) 浏览器启动缓存
```python
# 考虑使用单例模式复用浏览器实例
class BrowserPool:
    _instance = None
    _browser = None

    @classmethod
    def get_context(cls):
        if cls._browser is None:
            cls._browser = launch_browser()
        return cls._browser.new_context()
```

#### b) 响应式等待优化
```python
# 使用 Playwright 的事件而不是轮询
page.wait_for_event('response', lambda r: 'api' in r.url)
```

---

### 12. 文档完善

**建议添加**:

1. **CONTRIBUTING.md**:
```markdown
# Contributing to NotebookLM Skill

## Development Setup
1. Fork and clone
2. Create virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Install dev dependencies: `pip install -r requirements-dev.txt`

## Code Style
- Use Black for formatting
- Use Ruff for linting
- Type hints encouraged

## Testing
- Run tests: `pytest`
- Coverage: `pytest --cov=scripts`
```

2. **ARCHITECTURE.md**:
- 说明项目结构
- 模块职责
- 数据流向
- 扩展指南

---

### 13. 类型提示

**建议**: 添加完整的类型注解
```python
from typing import Optional, List, Dict, Any

def ask_notebooklm(
    question: str,
    notebook_url: str,
    headless: bool = True
) -> Optional[str]:
    """
    Ask a question to NotebookLM

    Args:
        question: Question to ask
        notebook_url: NotebookLM notebook URL
        headless: Run browser in headless mode

    Returns:
        Answer text from NotebookLM, or None if failed

    Raises:
        ValueError: If notebook_url is invalid
        RuntimeError: If browser automation fails
    """
    ...
```

---

### 14. 配置验证

**建议**: 添加配置验证
```python
# scripts/config_validator.py
from pathlib import Path

def validate_config():
    """Validate configuration before running"""
    errors = []

    # Check Chrome path
    chrome_path = get_chrome_path()
    if not chrome_path or not Path(chrome_path).exists():
        errors.append("Chrome not found. Please install Google Chrome.")

    # Check data directory permissions
    if not DATA_DIR.exists():
        try:
            DATA_DIR.mkdir(parents=True)
        except PermissionError:
            errors.append(f"Cannot create data directory: {DATA_DIR}")

    if errors:
        for error in errors:
            print(f"❌ {error}")
        return False
    return True
```

---

## 📊 优先级总结

### 立即修复 (本周)
1. ✅ 跨平台 Chrome 路径
2. ✅ JavaScript 注入问题 (ask_gemini.py)
3. ✅ 更新 .gitignore

### 近期优化 (本月)
4. 代码重复抽取
5. 错误处理改进
6. 依赖版本更新
7. 超时配置统一

### 长期增强 (可选)
8. 添加测试套件
9. 日志系统
10. 环境变量配置
11. 性能优化
12. 文档完善
13. 类型提示
14. 配置验证

---

## 🎯 建议的实施顺序

**Week 1**:
- [x] 修复跨平台兼容性
- [x] 修复 JavaScript 注入
- [x] 更新 .gitignore

**Week 2**:
- [ ] 抽取公共代码到 `common/`
- [ ] 统一错误处理
- [ ] 添加日志系统

**Week 3**:
- [ ] 添加基础测试
- [ ] 添加类型提示
- [ ] 更新文档

**Week 4**:
- [ ] 性能优化
- [ ] 配置验证
- [ ] 发布 v2.0

---

## 📝 备注

- 所有修改应保持向后兼容
- 优先保证现有功能稳定
- 新功能应有对应文档和测试
- 重大变更前应征求用户反馈

生成工具: Claude Code + NotebookLM Skill
版本: 1.3.0
