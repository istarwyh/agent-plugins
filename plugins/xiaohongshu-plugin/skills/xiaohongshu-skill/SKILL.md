---
name: xiaohongshu-skill
description: Open, log in, browse, search, publish posts, and interact with Xiaohongshu (小红书) using Chrome DevTools MCP. Handles login flow, feed browsing, content search, post viewing, and content publishing.
---

# Xiaohongshu (小红书) Browser Automation

Automate interactions with Xiaohongshu web version via Chrome DevTools MCP tools.

## Prerequisites

- Chrome DevTools MCP server connected (`chrome-devtools-mcp`)
- Chrome browser running with remote debugging enabled

## Step 0: Ensure Chrome is Running with Remote Debugging

**This step is CRITICAL and must be done FIRST before any MCP tool calls.** Chrome 145+ requires `--user-data-dir` to be a non-default path for remote debugging to work — even on ARM-native builds. The default path (`~/Library/Application Support/Google/Chrome`) is always rejected.

### Quick Check

Run this Bash command first to see if Chrome debugging is already available:

```bash
curl -s http://127.0.0.1:9222/json/version 2>&1 | head -3
```

If it returns a JSON with `"Browser"`, Chrome is ready — skip to Step 1.

### If Chrome is NOT ready, run the automated setup:

```bash
# 1. Kill existing Chrome
killall -9 "Google Chrome" 2>/dev/null
sleep 4

# 2. Create a symlinked user-data-dir that reuses the original profile
#    This preserves all cookies, extensions, and login sessions
#    while satisfying Chrome's "non-default directory" requirement.
ORIGINAL_DIR="$HOME/Library/Application Support/Google/Chrome"
LINKED_DIR="/tmp/chrome-linked-profile"
rm -rf "$LINKED_DIR"
mkdir -p "$LINKED_DIR"
ls "$ORIGINAL_DIR" | while read item; do
  ln -s "$ORIGINAL_DIR/$item" "$LINKED_DIR/$item" 2>/dev/null
done

# 3. Launch Chrome with remote debugging using the symlinked dir
arch -arm64 /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$LINKED_DIR" 2>/dev/null &

# 4. Wait and verify
sleep 6
curl -s http://127.0.0.1:9222/json/version | head -3
```

### Why this works

| Problem | Cause | Solution |
|---------|-------|----------|
| `DevTools remote debugging requires a non-default data directory` | Chrome 145+ refuses to enable debugging on the default profile path | Use `--user-data-dir` pointing to a different path |
| New profile loses cookies/extensions/login | Using a fresh `--user-data-dir` creates an empty profile | Symlink all contents from the original Chrome directory into the new path |
| `Could not find DevToolsActivePort` | MCP plugin looks for this file, but Chrome didn't create it | Ensure `--user-data-dir` is set (this is what triggers the file creation at the non-default path) |
| Rosetta warning on ARM Mac | x86 Chrome binary running via Rosetta | Use `arch -arm64` to force ARM execution, or install ARM-native Chrome |

### Important notes

- You MUST kill ALL Chrome processes before restarting — leftover processes lock the profile directory.
- After restarting Chrome, the MCP `chrome-devtools-mcp` server may need to reconnect. If MCP tools fail, try `list_pages` first to trigger reconnection.
- The symlinked profile dir must be recreated each session since `/tmp` is cleared on reboot.

## Workflow

### 1. Open Xiaohongshu

```
new_page(url: "https://www.xiaohongshu.com")
```

If navigation times out, use `list_pages` to check if the page loaded anyway, then `select_page` to select it.

### 2. Check Login Status

Take a snapshot and check for login indicators:
- **Not logged in**: Left sidebar shows "登录" button, no "我" menu item
- **Logged in**: Left sidebar shows "我" menu item with user avatar

### 3. Login Flow

If not logged in, click the "登录" button. A modal will appear with two options:

#### Option A: QR Code Login (Recommended)
1. Take a screenshot so the user can see the QR code
2. Ask the user to scan the QR code with their Xiaohongshu App or WeChat
3. Wait for the user to confirm they've scanned
4. Take a screenshot to verify login success
5. If QR code expires, click to refresh it

#### Option B: Phone Number Login
1. Click the phone number input field ("+86 输入手机号")
2. Fill in the user's phone number using `fill(uid, value)`
3. Click "获取验证码" button
4. Ask the user for the verification code
5. Fill in the verification code
6. Click "登录" button

### 4. Browse Feed

After login, the home feed (`/explore`) shows recommended content cards. Each card contains:
- Post thumbnail image (click to open)
- Post title
- Author name and link
- Like count

Use `take_snapshot()` to get the current feed content.

### 5. Search Content

1. Click the search box at the top (textbox "搜索小红书")
2. Type search query using `fill(uid, query)`
3. Press Enter or click search
4. Parse search results from the snapshot

### 6. View Post Details

1. Click on a post link from the feed or search results
2. Wait for the post page to load
3. Take a snapshot to extract:
   - Post title and content text
   - Images/videos
   - Author info
   - Like, collect, comment counts
   - Comments section

### 7. Publish a Post (写文字模式)

The creator center is at `https://creator.xiaohongshu.com/publish/publish`. There are multiple publish modes: 上传视频 (Upload Video), 上传图文 (Upload Image+Text), 写文字 (Write Text), 写长文 (Write Long Article).

The "写文字" mode creates text-based image cards — ideal for text-heavy posts without needing to prepare images.

#### Step 1: Navigate to Creator Center

Click the "发布" link in the left sidebar on the main site. This opens the creator center in a **new tab**.

```
click(uid_of_发布_link)
list_pages()          # Find the new creator tab
select_page(pageId)   # Switch to it
```

**Important**: The "发布" link opens `creator.xiaohongshu.com` in a new tab. You must use `list_pages` + `select_page` to switch to it.

#### Step 2: Enter Text Content

1. Take a snapshot to find the textbox element in the "写文字" editor
2. Click the textbox to focus it
3. Use `type_text` to input the post content

```
click(uid_of_textbox)
type_text(text: "Your post content here...")
```

**Note**: The text card editor splits long content across multiple pages automatically. Each page becomes a separate image card.

#### Step 3: Generate Images

Click "生成图片" (Generate Images) to convert text into image cards.

```
click(uid_of_生成图片)
```

Wait for image generation to complete — look for "下一步" (Next Step) button and card style options.

#### Step 4: Choose Card Style

The editor offers multiple card styles: 基础, 插图, 备忘, 边框, 涂鸦, 清新, 涂写, 便签, 光影, 简约.

1. Click on a style name to preview it
2. Click "下一步" (Next Step) to proceed

```
click(uid_of_style)    # e.g., 简约
click(uid_of_下一步)
```

#### Step 5: Fill in Title and Description

After clicking "下一步", the full publish form appears with:

- **Title field**: textbox with placeholder "填写标题会有更多赞哦" — fill using `fill(uid, title)`
- **Description field**: multiline textbox — already pre-filled with the text content from Step 2
- **Recommended hashtags**: clickable tag elements like `#小红书科技AMA`, `#开发者模式` etc.
- **Activity topics**: optional topic tags to join campaigns

```
fill(uid_of_title_textbox, "Your Post Title")
click(uid_of_hashtag)   # Optional: add a recommended hashtag
```

#### Step 6: Configure Settings (Optional)

The publish form also has these optional settings:

| Setting | Description |
|---------|-------------|
| 加入合集 | Add to a collection |
| 原创声明 | Declare as original content (checkbox) |
| 添加内容类型声明 | Add content type declaration |
| 添加地点 | Add location |
| 选择群聊 | Select group chat to share |
| 允许合拍 | Allow duets (checked by default) |
| 允许正文复制 | Allow text copying (checked by default) |
| 公开可见 | Public visibility (default) |
| 定时发布 | Schedule publish time (checkbox) |

#### Step 7: Publish

Click the "发布" button to publish the post.

```
click(uid_of_发布_button)
```

After publishing, the URL will change to include `published=true` and the page returns to the upload interface. Verify success by checking:
- URL contains `published=true`
- Page shows the upload interface (上传视频/上传图文 tabs)

#### Complete Publish Flow Summary

```
1. click("发布" link)           → Opens creator center in new tab
2. list_pages + select_page     → Switch to creator tab
3. take_snapshot                → Find textbox UID
4. click(textbox) + type_text   → Input content
5. click("生成图片")             → Convert to image cards
6. wait_for("下一步")           → Wait for generation
7. click(style) + click("下一步") → Choose style, proceed
8. fill(title_textbox, title)   → Set post title
9. click(hashtag)               → Add topic tags (optional)
10. click("发布")                → Publish the post
11. Verify URL has published=true
```

### 8. View User Profile

1. Click on a user's name link
2. Wait for profile page to load
3. Extract: username, bio, follower/following counts, post list

## Key Details

- **URL Pattern**: `https://www.xiaohongshu.com/explore` (home feed), `https://www.xiaohongshu.com/explore/{post_id}` (post detail), `https://creator.xiaohongshu.com/publish/publish` (creator center)
- **Login persistence**: The user's browser cookies/session are available, so login may persist across sessions
- **Rate limiting**: Be mindful of request frequency; add reasonable pauses between rapid interactions
- **Dynamic content**: The feed uses infinite scroll; scroll down with `evaluate_script` to load more content
- **Popups**: After login, promotional popups may appear; close them by clicking the X button or pressing Escape
- **QR code expiration**: QR codes expire after a short period; if login fails, refresh and retry

## Common Issues

| Issue | Solution |
|-------|----------|
| MCP tools return "No such tool available" | Chrome was restarted but MCP server lost connection. Try calling `list_pages` to trigger reconnection. If that also fails, the MCP server process itself may need restart (outside of this skill's scope). |
| `DevToolsActivePort` not found | Chrome is not running with `--user-data-dir`. Follow Step 0 to restart Chrome properly. |
| Chrome debugging port not listening | Run Step 0 setup. Make sure ALL Chrome processes are killed first (`killall -9 "Google Chrome"`), wait 4 seconds, then restart. |
| `open -a Chrome --args` ignores flags | macOS `open -a` may drop `--args` flags. Always use the binary path directly: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --remote-debugging-port=9222 ...` |
| Lost login/cookies after Chrome restart | You used a fresh `--user-data-dir` without symlinks. Follow Step 0's symlink approach to preserve the original profile. |
| Navigation timeout | Check `list_pages` — the page may have loaded despite the timeout |
| QR code expired | Refresh the page or click to regenerate the QR code |
| Login modal not appearing | Try clicking the "登录" text in the sidebar |
| Content not loading | The page may use lazy loading; scroll down with `evaluate_script(() => window.scrollBy(0, 500))` |
| Element not interactive | Wait briefly and retry, or take a new snapshot to get updated UIDs |
| Creator center opens in new tab | Use `list_pages` to find the tab, then `select_page` to switch to it |
| Text card content reversed | This is a known rendering quirk in the text card editor; the final published images display correctly |
| "发布" button not responding | Ensure the title field is filled — it may be required before publishing |
| Image generation stuck | Wait and retry; check for "图片生成中" text, then wait for "下一步" to appear |
