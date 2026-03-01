# Xiaohongshu Web Reference

## Page Structure

### Home Feed (`/explore`)

The home feed displays content in a masonry grid layout with these categories in the top navigation:
- 推荐 (Recommended)
- 穿搭 (Fashion)
- 美食 (Food)
- 彩妆 (Makeup)
- 影视 (Movies/TV)
- 职场 (Career)
- 情感 (Emotion)
- 家居 (Home)
- 游戏 (Gaming)
- 旅行 (Travel)
- 健身 (Fitness)

### Left Sidebar

- 发现 (Discover) — Home feed
- 发布 (Publish) — Opens creator center
- 通知 (Notifications)
- 我 (My Profile) — Only visible when logged in

### Top Bar

- Logo (links to home)
- Search box
- 创作中心 (Creator Center)
- 业务合作 (Business Cooperation)

## Selectors and Element Identification

Use `take_snapshot()` to get the accessibility tree with UIDs. Key elements:

| Element | Description | How to Find |
|---------|-------------|-------------|
| Login button | "登录" button in sidebar | Look for `button "登录"` in snapshot |
| Search box | Top search input | Look for `textbox` with search-related label |
| Feed cards | Content posts | Links with `/explore/` in URL |
| Author links | User profile links | Links with `/user/profile/` in URL |
| Category tabs | Content categories | StaticText elements in the tab bar area |

## Login Modal Structure

When the login modal opens:

**Left side — QR Code:**
- QR code image for scanning
- Text: "可用 小红书 或 微信 扫码"
- Link: "小红书如何扫码"

**Right side — Phone Login:**
- Country code selector (+86)
- Phone number input
- Verification code input
- "获取验证码" (Get code) button
- "登录" (Login) button
- Checkbox: user agreement
- Link: "新用户可直接登录"

## Content Extraction Tips

### Extracting Post Content
```javascript
// Use evaluate_script to extract structured data
() => {
  return {
    title: document.querySelector('.title')?.textContent,
    content: document.querySelector('.desc')?.textContent,
    likes: document.querySelector('.like-wrapper .count')?.textContent
  }
}
```

### Scrolling for More Content
```javascript
// Scroll down to trigger lazy loading
() => {
  window.scrollBy(0, 800);
  return document.documentElement.scrollTop;
}
```

### Checking Login State
```javascript
() => {
  // If "我" menu item exists, user is logged in
  const sidebarItems = document.querySelectorAll('a');
  for (const a of sidebarItems) {
    if (a.textContent.includes('我')) return true;
  }
  return false;
}
```
