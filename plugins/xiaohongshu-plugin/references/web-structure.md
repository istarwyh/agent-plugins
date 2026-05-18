# 小红书 Web 页面结构参考

## 首页 (`/explore`)

### Feed 布局

瀑布流网格布局，顶部分类导航：
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

### 左侧边栏

- 发现 (Discover) — 首页 Feed
- 发布 (Publish) — 打开创作中心
- 通知 (Notifications)
- 我 (My Profile) — 仅登录后可见

### 顶部栏

- Logo（链接到首页）
- 搜索框
- 创作中心 (Creator Center)
- 业务合作 (Business Cooperation)

## 元素定位

使用 `take_snapshot()` 获取无障碍树和 UID。关键元素：

| 元素 | 说明 | 定位方式 |
|------|------|----------|
| 登录按钮 | 侧边栏 "登录" | snapshot 中找 `button "登录"` |
| 搜索框 | 顶部搜索输入 | 找 `textbox` + 搜索相关 label |
| Feed 卡片 | 内容帖子 | URL 含 `/explore/` 的链接 |
| 作者链接 | 用户主页 | URL 含 `/user/profile/` 的链接 |
| 分类标签 | 内容分类 | 标签栏区域的 StaticText 元素 |

## 登录弹窗结构

**左侧 — 二维码：**
- 二维码图片（扫码登录）
- 文字: "可用 小红书 或 微信 扫码"
- 链接: "小红书如何扫码"

**右侧 — 手机号登录：**
- 国家代码选择器 (+86)
- 手机号输入框
- 验证码输入框
- "获取验证码" 按钮
- "登录" 按钮
- 用户协议勾选框（**在 Shadow DOM 中**，需用坐标点击）
- 链接: "新用户可直接登录"

**注意**：协议勾选框（"已阅读并同意《用户协议》和《隐私政策》"）位于 Shadow DOM 内，`document.querySelectorAll` 无法找到。需要通过截图确定坐标后使用 `Input.dispatchMouseEvent` 点击。

## 创作中心 (`https://creator.xiaohongshu.com/publish/publish`)

### 发布页面结构

**初始状态**：显示两个入口标签
- "上传视频" — 视频发布模式
- "上传图文" — 图文发布模式

**图文模式**：点击"上传图文"后
- "上传图片，或写文字生成图片" 提示
- 图片上传区域（拖拽或点击）
- "文字配图" 按钮 — 激活文字卡片编辑器

**文字配图编辑器**：
- `.tiptap.ProseMirror` — tiptap 富文本编辑器
- 支持换行、emoji、话题标签
- "生成图片" 按钮 — 将文字转为图片卡片
- "再写一张" 按钮 — 添加多张卡片

**图片预览页**：
- 生成的图片卡片预览
- "下一步" 按钮 — 进入发布编辑页

**发布编辑页**：
- `input[placeholder*="标题"]` — 标题输入框（≤20 字）
- 正文预览区域
- "发布" 按钮：优先查 `button.bg-red`/`button.ce-btn.bg-red`，新版可能封装为 `<xhs-publish-btn>`
- 发布成功标志：URL 跳转到 `publish/success` 路径，或页面显示"发布成功"
- 标题输入需用 `nativeInputValueSetter` 模式（React 状态管理）

### 自定义封面上传流程

使用 Chrome DevTools `upload_file` 工具或 CDP 直接上传：

**方式1：MCP 工具**
1. 导航到创作中心发布页
2. 点击"上传图文"
3. 找到图片上传区域的 `input[type="file"]`（accept 含 `.jpg,.jpeg,.png,.webp`）
4. 使用 `upload_file` 上传封面图
5. 等待图片处理完成
6. 点击"下一步"进入编辑页

**方式2：CDP 直接上传**（MCP 不可用时）
1. 通过 `Runtime.evaluate` 获取 file input 的 `objectId`
2. 调用 `DOM.setFileInputFiles` 设置文件路径
3. 等待图片处理完成（页面会显示预览）
4. 滚动到底部找到"下一步"按钮并点击

## 内容提取

### 提取帖子内容
```javascript
() => {
  return {
    title: document.querySelector('.title')?.textContent,
    content: document.querySelector('.desc')?.textContent,
    likes: document.querySelector('.like-wrapper .count')?.textContent
  }
}
```

### 滚动加载更多
```javascript
() => {
  window.scrollBy(0, 800);
  return document.documentElement.scrollTop;
}
```

### 检测登录状态
```javascript
() => {
  const sidebarItems = document.querySelectorAll('a');
  for (const a of sidebarItems) {
    if (a.textContent.includes('我')) return true;
  }
  return false;
}
```
