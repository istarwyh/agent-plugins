# 小红书发布排障经验库

发布失败时先查这个文件，再决定是否重试。原则：无法确认发布结果时不要连续重试，先验证当前页面或个人主页，避免重复笔记。

## 使用顺序

1. **先分段定位**：登录 → 填表 → 图片上传 → 发布按钮 → 成功页验证。
2. **先看页面状态**：读取当前 URL、`document.body.innerText`、关键元素数量。
3. **先确认再重试**：CLI 超时或返回不确定状态时，先搜索标题或让用户检查主页。
4. **记录新坑**：按“症状 / 信号 / 排查 / 处理 / 预防”追加到“经验条目”。

## 快速诊断命令

```bash
python3 xiaohongshu-skills/scripts/cli.py check-login
python3 xiaohongshu-skills/scripts/cli.py fill-publish --title-file t.txt --content-file c.txt --images /abs/img.png
python3 xiaohongshu-skills/scripts/cli.py click-publish
```

发布页内可用的状态探针：

```javascript
(() => ({
  url: location.href,
  success: location.href.includes('/publish/success') || document.body.innerText.includes('发布成功'),
  tabs: Array.from(document.querySelectorAll('div.creator-tab')).map((tab, i) => {
    const rect = tab.getBoundingClientRect();
    const style = getComputedStyle(tab);
    return { i, text: tab.textContent.trim(), left: rect.left, top: rect.top, width: rect.width, height: rect.height, opacity: style.opacity };
  }),
  publishButtons: document.querySelectorAll('button.bg-red, button.ce-btn.bg-red').length,
  customPublishButton: !!document.querySelector('xhs-publish-btn'),
}))()
```

## 经验条目

### XHS-PUB-001：CLI 发布超时

**症状**：`publish_content` 或 `cli.py publish` 超时，没有明确成功或失败。

**信号**：命令无返回，但浏览器可能已经提交过发布动作。

**排查**：
- 搜索刚发布的标题，或让用户检查小红书 App 个人主页。
- 检查当前发布页是否已经跳转到 `/publish/success` 或显示“发布成功”。

**处理**：
- 未确认失败前不要重试。
- 用户确认主页没有笔记后，才重新执行发布。

**预防**：优先使用分步发布：`fill-publish` → 用户确认 → `click-publish`。

### XHS-PUB-002：找不到“上传图文”Tab

**症状**：`没有找到发布 TAB - 上传图文`。

**信号**：调试信息里能看到多个 `div.creator-tab`，其中“上传图文”有透明副本或被移出视口。

**排查**：运行状态探针，重点看 `opacity`、`left/top`、`width/height`。

**处理**：点击 Tab 时只选择真实可见元素：
- `width/height > 0`
- `left/top >= 0`
- `display !== 'none'`
- `visibility !== 'hidden'`
- `opacity >= 0.5`

**预防**：不要只按文本取第一个匹配元素；页面会为埋点或热区生成透明副本。

### XHS-PUB-003：找不到发布按钮

**症状**：表单已填写、预览正常，但 `click-publish` 报 `未找到发布按钮`。

**信号**：页面没有普通 `button.bg-red`，但存在 `<xhs-publish-btn>`：

```javascript
document.querySelectorAll('xhs-publish-btn').length
```

**原因**：新版发布按钮封装在 closed Shadow DOM，自定义元素内部的真实按钮无法被普通选择器访问。

**处理**：对宿主元素派发页面自身使用的发布事件：

```javascript
(() => {
  const btn = document.querySelector('xhs-publish-btn');
  if (!btn) return { ok: false, reason: 'xhs-publish-btn not found' };
  if (btn.getAttribute('submit-disabled') === 'true') return { ok: false, reason: 'disabled' };
  btn.scrollIntoView({ block: 'center' });
  btn.dispatchEvent(new CustomEvent('publish', { bubbles: true, composed: true }));
  return { ok: true };
})()
```

**验证**：等待 URL 进入 `/publish/success`，或页面出现“发布成功”。

**预防**：`click-publish` 应先尝试普通按钮，再 fallback 到 `<xhs-publish-btn>` 事件。

### XHS-PUB-004：成功判断不要依赖命令返回

**症状**：发布动作触发后，命令返回慢、超时或页面仍在跳转。

**可靠信号**：

```javascript
location.href.includes('/publish/success') || document.body.innerText.includes('发布成功')
```

**处理**：只有看到成功页或用户确认主页出现笔记，才把本地草稿标为 `published`。

**预防**：发布工具应在点击后等待成功页；未检测到成功页时返回“不确定”而不是盲目重试。

## 新经验模板

```markdown
### XHS-PUB-00N：一句话描述

**症状**：用户或 CLI 看到什么。

**信号**：日志、DOM、URL、截图里有什么证据。

**排查**：按什么顺序确认。

**处理**：当前版本的可执行 fallback。

**预防**：脚本或 skill 应怎样避免复发。
```
