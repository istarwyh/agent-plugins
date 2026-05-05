---
name: xhs-login
description: |
  管理小红书登录状态：检查是否已登录、二维码扫码登录、手机验证码登录、退出登录。
  当用户提到登录、扫码、账号、切换账号、退出登录、登录状态检查时使用。
---

CLI 路径：`python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py`

## 执行流程

### 1. 检查登录状态

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py check-login
```

- `{"logged_in": true}` → 告知用户已登录
- `{"logged_in": false, "qrcode_path": ..., "qrcode_image_url": ...}` → 自动返回了二维码，进入步骤 2

### 2. 登录

**方式 A：二维码登录（推荐）**

`check-login` 未登录时已自动返回二维码。展示给用户：
- 图片：`qrcode_image_url` 或打开 `qrcode_path` 文件
- 链接：`qr_login_url`（如有）

然后等待扫码完成：
```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py wait-login --timeout 120
```

或重新获取二维码：
```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py get-qrcode
```

**方式 B：手机验证码**

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py send-code --phone 13800138000
```

询问用户验证码后：
```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py verify-code --code 123456
```

### 3. 退出登录

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py delete-cookies
```

## 约束

- 验证码发送受限时自动切换为二维码登录
- 不要频繁重复登录/退出，避免风控

## 兜底（Chrome DevTools MCP）

CLI 失败时（Extension 未连接）：

```bash
bash {baseDir}/../../scripts/ensure-chrome-debug.sh
```

- `navigate_page` → `https://www.xiaohongshu.com`
- `take_snapshot` → 找到登录按钮 → `click`
- `take_screenshot` → 展示二维码给用户扫码
- 扫码后 `navigate_page` 刷新 → `evaluate_script` 检查登录状态
