---
name: setup-xhs
description: |
  安装部署小红书自动化环境：Python CLI 引擎 + Chrome 浏览器扩展。
  当用户第一次使用小红书功能、提到安装/部署/配置小红书、环境搭建、CLI 命令报错、或 check-login 返回 connection/bridge 错误时使用。
---

## 前置条件

- macOS 或 Linux
- Python >= 3.11
- Google Chrome 浏览器

## 安装流程

### 1. 安装 Python 依赖

```bash
cd {baseDir}/../../xiaohongshu-skills && uv sync
```

如果没有 `uv`，先安装：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装 Chrome 扩展

引导用户在 Chrome 中加载开发者扩展：

1. 打开 Chrome，地址栏输入 `chrome://extensions/`
2. 右上角打开「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择目录：`{baseDir}/../../xiaohongshu-skills/extension/`
5. 确认扩展「XHS Bridge」已启用

### 3. 验证安装

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py check-login
```

- 返回 `{"logged_in": ...}` → 安装成功
- 返回 connection/bridge 错误 → 检查扩展是否启用、Chrome 是否打开

### 4. 登录

验证通过后，引导用户执行 `/xhs-login` 完成登录。

## 环境检查

```bash
bash {baseDir}/../../scripts/check_env.sh
```

## 故障排查

| 问题 | 解决 |
|---|---|
| `uv: command not found` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `python3: command not found` | 安装 Python 3.11+：`brew install python@3.11` |
| Bridge 连接失败 | 确认 Chrome 扩展已启用，Chrome 已打开 |
| 扩展报错 | 在 `chrome://extensions/` 查看扩展错误日志 |
| CLI 超时 | 确认小红书页面已加载，尝试刷新页面 |

## 不需要的东西

- 不需要 Docker
- 不需要 `--remote-debugging-port`
- 不需要 MCP server
- 不需要 Go 编译环境
