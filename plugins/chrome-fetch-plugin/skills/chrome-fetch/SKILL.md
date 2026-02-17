---
name: chrome-fetch
description: Fetch web page content using Chrome DevTools MCP when WebFetch fails, returns domain verification errors, or the page requires authentication/JS rendering. Uses the user's running Chrome browser via autoConnect. (agent)
---

# Chrome Fetch Skill

Fetch web content through the user's Chrome browser when WebFetch cannot (domain restrictions, authentication, SPAs needing JS rendering).

## Workflow

1. `new_page(url)` to open the target URL in a new tab
2. `wait_for(text, timeout: 15000)` with an expected keyword — if it times out, proceed anyway
3. Extract content via `evaluate_script`:
   ```
   () => { const main = document.querySelector('main, article, [role="main"], .content, #content'); return (main || document.body).innerText; }
   ```
   For long pages, append `.substring(0, 50000)` to truncate.
4. If extraction returns empty (shadow DOM, iframes), fall back to `take_snapshot()` and read `StaticText` entries
5. `close_page(pageId)` to clean up (skip if it's the only open page)

## Key Details

- Requires chrome-devtools-mcp with `--autoConnect` and Chrome 144+
- The user's cookies/sessions are available, so authenticated pages work
- For complex SPAs, you may need to wait longer or interact (click, scroll) before content appears
