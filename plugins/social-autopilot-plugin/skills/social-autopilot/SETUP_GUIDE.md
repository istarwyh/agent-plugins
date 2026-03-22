# Meta API 配置全流程引导

本文档引导非技术用户完成 Meta Graph API 的配置，以实现 Facebook/Instagram 自动排期发布。

> **此步骤为可选**。即使不配置 Meta API，系统仍可正常运行全链路到「生成帖子草稿+卡片图」，
> 用户可手动通过 Meta Business Suite 发布。

---

## 概览

需要完成的步骤：
1. 创建 Meta 开发者账号和 App
2. 获取 Facebook Page 的长期 Token
3. 获取 Instagram Business Account ID
4. 申请权限（需要 App Review）
5. 将凭证填入 .env

**预计耗时**: 首次配置约 30 分钟 + App Review 等待 1~4 周

---

## 第1步：创建 Meta App

1. 访问 https://developers.facebook.com/
2. 点击右上角 "Get Started" 或 "My Apps"
3. 点击 "Create App"
4. 选择 "Business" 类型
5. 填写 App 名称（如 "My Store Social Bot"）和联系邮箱
6. 创建完成后，在 Dashboard 记录 **App ID** 和 **App Secret**

## 第2步：添加产品

1. 在 App Dashboard 左侧菜单，点击 "Add Product"
2. 找到 "Facebook Login" 并点击 "Set Up"
3. 找到 "Instagram Graph API" 并点击 "Set Up"（如果可见）

## 第3步：获取 User Token

1. 访问 Graph API Explorer: https://developers.facebook.com/tools/explorer/
2. 选择你的 App
3. 点击 "Generate Access Token"
4. 勾选以下权限：
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
   - `instagram_basic`
   - `instagram_content_publish`
5. 点击 "Generate Access Token"，授权弹窗中允许访问你的 Page
6. 复制生成的 **短期 User Token**

## 第4步：换取长期 Token

在浏览器中访问以下 URL（替换实际值）：

```
https://graph.facebook.com/v19.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id={你的App ID}&
  client_secret={你的App Secret}&
  fb_exchange_token={短期User Token}
```

返回的 JSON 中包含 `access_token`，这是 **60天有效** 的长期 User Token。

## 第5步：获取 Page Access Token（永久有效）

```
https://graph.facebook.com/v19.0/me/accounts?access_token={长期User Token}
```

返回结果中找到你的 Page，记录：
- `id` → 这是 **META_PAGE_ID**
- `access_token` → 这是 **META_PAGE_ACCESS_TOKEN**（永久有效）

## 第6步：获取 Instagram Business Account ID

```
https://graph.facebook.com/v19.0/{META_PAGE_ID}?fields=instagram_business_account&access_token={Page Token}
```

返回的 `instagram_business_account.id` 就是 **META_IG_USER_ID**。

> **注意**: 你的 Instagram 账号必须是 Business 或 Creator 账号，且已关联到 Facebook Page。

## 第7步：申请 App Review

`instagram_content_publish` 和 `pages_manage_posts` 权限需要通过 Meta 的 App Review。

1. 在 App Dashboard → App Review → Permissions and Features
2. 找到 `instagram_content_publish`，点击 "Request Advanced Access"
3. 填写使用说明（示例）：
   > "We use this permission to automatically schedule and publish product-related
   > news posts to our Instagram business account. Posts are pre-generated and
   > reviewed before publishing."
4. 提交审核，等待 1~4 周

**在审核通过之前**：你可以在 "Development Mode" 下测试，
但只能用 App 管理员/测试员账号发帖。

## 第8步：填写 .env

将以下值填入 `~/social-autopilot/.env`：

```
META_PAGE_ID=你的Page ID
META_PAGE_ACCESS_TOKEN=你的永久Page Token
META_IG_USER_ID=你的Instagram Business Account ID
```

## 验证

运行以下命令验证配置：

```bash
python scripts/run.py schedule_meta.py --dry-run
```

应显示 "Token状态: 有效" 和对应的权限列表。

---

## Token 续期

Page Access Token 通过第5步获取的是**永久有效**的，但以下情况会失效：
- 用户更改 Facebook 密码
- 用户取消 App 授权
- App 被 Meta 禁用

如果 Token 失效，重新执行第3~5步即可。

## 常见问题

**Q: 我的 Instagram 不是 Business 账号怎么办？**
A: Instagram → 设置 → 账号 → 切换到专业帐号 → 选择"商家"

**Q: App Review 被拒怎么办？**
A: 常见原因是使用说明不够详细。补充截图和具体使用场景后重新提交。

**Q: 不想配置 Meta API 可以吗？**
A: 完全可以。系统会生成帖子草稿和卡片图片，你可以手动通过 Meta Business Suite 发布。
