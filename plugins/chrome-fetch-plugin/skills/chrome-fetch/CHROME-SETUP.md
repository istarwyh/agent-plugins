# Chrome DevTools MCP 设置指南

## 问题说明
chrome-devtools-mcp 的 `--autoConnect` 功能有时不稳定，需要手动确保 Chrome 以调试模式运行。

## 解决方案

### 方法 1：使用启动脚本
```bash
# 运行提供的启动脚本
./start-chrome-debug.sh
```

### 方法 2：手动启动
```bash
# 1. 完全关闭 Chrome
pkill -f "Google Chrome"

# 2. 启动调试模式 Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir=/tmp/chrome-debug

# 3. 启动 MCP
npm exec chrome-devtools-mcp@latest --no-usage-statistics
```

### 方法 3：添加到 shell 配置
在 ~/.zshrc 或 ~/.bashrc 中添加：
```bash
alias chrome-debug='/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug'
alias chrome-mcp='npm exec chrome-devtools-mcp@latest --no-usage-statistics'
```

## 验证连接
```bash
# 检查 Chrome 调试端口
curl http://localhost:9222/json/version

# 应该返回类似：
# {
#   "Browser": "Chrome/145.0.7632.160",
#   "Protocol-Version": "1.3",
#   ...
# }
```

## 自动化方案
1. 创建 Chrome 调试模式的 macOS 自动化应用
2. 设置登录时自动启动
3. 使用 launchd 管理服务

## 故障排除
- 如果端口被占用，尝试其他端口（9223, 9224）
- 检查防火墙设置
- 确保没有其他 Chrome 实例运行
