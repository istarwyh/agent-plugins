---
name: xhs-login
description: |
  管理小红书登录状态：检查是否已登录、二维码扫码登录、重置登录切换账号。
  当用户提到登录、扫码、账号、切换账号、退出登录、登录状态检查，或其他 skill 报告"未登录"需要先登录时使用。
---

## 执行流程

### 1. 检查登录状态

**方式一：MCP 工具**

调用 `check_login_status`（无参数），返回是否已登录及用户名。

**方式二：Chrome DevTools MCP（MCP 工具失败时）**

```bash
bash {baseDir}/../scripts/ensure-chrome-debug.sh
```

导航到小红书首页，用 `evaluate_script` 检查登录状态：

```javascript
() => {
  const links = document.querySelectorAll('a');
  for (const a of links) {
    if (a.textContent.includes('我')) return { loggedIn: true };
  }
  return { loggedIn: false };
}
```

- 已登录 → 告知用户当前登录账号
- 未登录 → 进入步骤 2

### 2. 扫码登录

**方式一：MCP 工具**

调用 `get_login_qrcode`（无参数）。MCP 工具返回两部分内容：
- 文本：超时提示（含截止时间）
- 图片：PNG 格式二维码（MCP image content type，Base64 编码）

**方式二：Chrome DevTools MCP（MCP 工具失败时）**

导航到小红书首页，`take_snapshot` 找到登录按钮并点击，`take_screenshot` 展示二维码给用户扫码。

**展示二维码**：MCP 返回的图片会通过客户端渲染给用户。如果客户端无法直接展示图片（如纯文本终端），则将 Base64 数据保存为临时 PNG 文件，告知用户文件路径让其手动打开：
```bash
# fallback: 保存二维码到临时文件
echo "<base64_data>" | base64 -d > /tmp/xhs-qrcode.png
open /tmp/xhs-qrcode.png   # macOS
xdg-open /tmp/xhs-qrcode.png  # Linux
```

提示用户：
- 打开小红书 App 扫描二维码
- 二维码有效期有限，过期需重新获取

扫码完成后，调用 `check_login_status` 确认登录成功。

### 3. 重新登录 / 切换账号

当用户要求重新登录或切换账号时：

1. 调用 `delete_cookies`（⚠️ 需用户确认）— 清除当前登录状态
2. 调用 `get_login_qrcode` — 获取新二维码
3. 引导用户扫码

## 约束

- `delete_cookies` 会清除登录状态，执行前必须确认
- 登录需要用户手动用手机 App 扫码，无法自动完成

## 失败处理

| 场景 | 处理 |
|---|---|
| MCP 工具不可用 | 自动切换到 Chrome DevTools MCP 路径 |
| 二维码超时 | 重新调用 `get_login_qrcode` 或重新截图 |
| 短信验证码拦截 | 见下方 fallback |
| Chrome DevTools 操作失败 | `take_snapshot` 查看页面结构重试 |

### Fallback：短信验证码拦截

MCP 服务使用的 Chrome 带有自动化特征，可能被小红书风控识别并触发短信验证码拦截（参见 [xiaohongshu-mcp#681](https://github.com/xpzouying/xiaohongshu-mcp/issues/681)）。

当扫码登录触发短信验证时，引导用户使用独立的 `xiaohongshu-login` 二进制完成登录：

```bash
cd ~/.claude/plugins/xiaohongshu-mcp
ROD_BROWSER_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ./xiaohongshu-login-darwin-arm64
```

该二进制会打开可见的 Chrome 窗口，使用真实浏览器 profile，不会触发拦截。登录完成后回到 Claude Code，调用 `check_login_status` 确认登录状态即可。

**判断是否触发拦截的信号**：用户报告扫码后要求输入短信验证码、页面显示安全验证、或扫码后长时间无响应。
