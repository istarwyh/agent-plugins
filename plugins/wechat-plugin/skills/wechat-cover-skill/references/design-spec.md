# WeChat Cover Design Specifications

## Color Constraints

**BANNED**: Blue (#3b82f6, #2563eb, #1d4ed8...), Purple (#8b5cf6, #a855f7, #7c3aed...), Indigo (#6366f1...), Violet, Cyan (#06b6d4, #0891b2...) — 全部禁止。

**APPROVED palettes**: Amber/Gold (#f59e0b, #eab308, #fbbf24), Coral/Warm Red (#e8553a, #ea580c, #e11d48), Emerald (#10b981, #059669), Dark Charcoal (#0f0e0b, #1a1710), Cream (#fef3c7, #fde68a), Slate/Neutral grays.

## Dimensions & Proportions

| Element | Ratio | Notes |
|---------|-------|-------|
| Overall container | **3.35:1** | Must be strictly maintained |
| Left area (main cover) | **2.35:1** | Primary visual area |
| Right area (朋友圈分享 cover) | **1:1** | Square share image |

- Container height auto-adjusts with width changes while keeping the ratio
- Internal elements scale relative to container size

## Layout Rules

- **朋友圈分享 cover (right):** Four large characters filling the area — two on top, two on bottom
- **Main cover (left):** Text is the visual focus, occupying at least **70%** of the space
- Both covers share the same background color and decorative elements
- Outer card must have **sharp (straight) corners** — no border-radius

## Responsive Behavior

- The 3.35:1 ratio must hold at all browser widths
- Typography and elements scale proportionally with container width
