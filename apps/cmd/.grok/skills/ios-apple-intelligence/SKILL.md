---
name: ios-apple-intelligence
description: >
  Integrate web apps with iOS and Apple Intelligence: Home Screen / PWA
  chrome, Safari Writing Tools, Share Sheet, safe areas, App Intents
  mapping, Image Playground and Visual Intelligence fallbacks via xAI,
  and the native Foundation Models / App Intents reference path. Use when
  the user asks for iOS, iPhone, iPad, Apple Intelligence, Siri, Writing
  Tools, Image Playground, App Intents, Foundation Models, PWA install,
  or "Eingliederung". Triggers on "iOS", "iPhone", "Apple Intelligence",
  "Siri", "Writing Tools", "Image Playground", "App Intents", "Foundation
  Models", "PWA", "Home Screen", "Safari", "Eingliederung".
metadata:
  short-description: "iOS + Apple Intelligence integration for web apps (PWA, Writing Tools, Intents, xAI fallback)"
user-invocable: false
---

# iOS + Apple Intelligence

Make the app feel native on iPhone/iPad and plug into Apple Intelligence
where the **web platform actually can**. This sandbox cannot compile Swift
or call on-device Foundation Models — ship a **web/PWA** that (1) unlocks
every Safari / iOS system surface and (2) mirrors Writing Tools, Image
Playground, Visual Intelligence, and App Intents with the **xAI API**
when Apple Intelligence is not in the room.

**Read `references/` for depth** (load on demand):

- `references/web-pwa.md` — Home Screen, viewport, safe area, share, standalone
- `references/native-apis.md` — Foundation Models, App Intents, Image Playground (Swift)

Pair with **`design-ui`** (tokens, no-slop), **`xai-api`** (Grok / Imagine),
**`auth`** (gate expensive media), **`og`** (share card). Do **not** pull
`building-games` unless the product is actually a game.

---

## 1. Decide the path (do this first)

| User is asking for… | You ship… |
| --- | --- |
| iOS / iPhone / Home Screen / PWA | Web app with the iOS contract below + installable chrome |
| Apple Intelligence / Writing Tools / Siri | Interactive studios that **use** the feature (not a marketing page) |
| Native Swift / Xcode / App Store binary | Honest limit: this sandbox is web-only. Document the Swift API in-app and implement the **web equivalent** with xAI |
| Both | One polished studio: iOS shell + live Intelligence tools + native reference |

Never dump a Swift snippet and call it done. Never pretend a `<textarea>`
*is* on-device Apple Intelligence — label the fallback clearly:
**„Auf diesem Gerät: Lumen (Grok). Auf dem iPhone: zusätzlich systemeigene Schreibwerkzeuge.“**

---

## 2. iOS contract (required on every iOS-facing app)

Do these in the **first scaffold**, not as polish.

1. **Viewport + safe area**
   ```ts
   { name: "viewport", content: "width=device-width, initial-scale=1, viewport-fit=cover" }
   ```
   Pad the shell with `env(safe-area-inset-top/bottom/left/right)`. Tab bars
   and large titles sit *inside* the safe area, not under the notch / home indicator.

2. **Apple web-app chrome** (keep the existing Grok PWA manifest/links):
   ```ts
   { name: "apple-mobile-web-app-capable", content: "yes" }
   { name: "apple-mobile-web-app-title", content: APP_NAME }
   { name: "apple-mobile-web-app-status-bar-style", content: "default" } // light UI
   { name: "mobile-web-app-capable", content: "yes" }
   { name: "theme-color", content: "#F2F2F7" } // iOS grouped background
   { name: "format-detection", content: "telephone=no" }
   ```

3. **Touch + type**
   - Tap targets ≥ 44×44 px
   - Form controls `font-size: 16px` (prevents iOS focus-zoom)
   - Never `user-select: none` on editable text (kills Writing Tools)
   - Never block the context menu on `textarea` / `contenteditable`

4. **Standalone detection** — `window.matchMedia("(display-mode: standalone)")`
   or `navigator.standalone`. Show an install tip only when *not* standalone.

5. **Share Sheet** — `navigator.share({ title, text, url })` with
   `navigator.clipboard.writeText` fallback. Primary export path on iOS.

6. **Writing Tools pass-through** — native Apple Intelligence Writing Tools
   appear on selected text in Safari / WKWebView (iOS 18.1+) for ordinary
   `textarea` and `contenteditable`. Use native fields. Do not replace them
   with a canvas or a `contenteditable` that hijacks `beforeinput`.

Full checklist: `references/web-pwa.md`.

---

## 3. Map Apple Intelligence → this app

Apple Intelligence is a **system**. Your app should expose the same verbs
users already know, then run them on-device when possible and via xAI here.

| System feature | Native (iOS 18.1–27) | Web / this sandbox |
| --- | --- | --- |
| Writing Tools | System menu on selection | Same verbs as buttons + Grok (`grok-4.5`); native menu still works in Safari |
| Image Playground | `ImagePlayground` API / sheet | xAI Imagine (`grok-imagine-image`), **auth-gated** |
| Visual Intelligence | Visual Intelligence / Foundation Models vision | Multimodal Grok (image + prompt), user-initiated |
| App Intents / Siri | `AppIntent` + schemas | In-app intent catalog + NL router (Grok) that executes the same actions |
| Foundation Models | `SystemLanguageModel` / `PrivateCloudComputeLanguageModel` | xAI chat; show the routing (on-device vs. Private Cloud vs. Grok) in the UI |
| Genmoji / Image Wand | System only | Out of scope — do not fake |

**Copy the Apple verbs exactly** (localized): Rewrite / Proofread / Summarize /
Key Points / List / Table / Friendly / Professional / Concise / Compose.
German UI: Umschreiben, Korrektur, Zusammenfassen, Kernpunkte, Liste,
Tabelle, Freundlich, Professionell, Prägnant, Verfassen.

### Server shape (xAI, user-initiated, capped)

Follow **`xai-api`**: `createServerFn`, `process.env.XAI_API_KEY`, never a
client key, `max_tokens` capped, no calls on keystroke or page load.

- Writing / intents / vision → `POST https://api.x.ai/v1/chat/completions`,
  model `grok-4.5`, `max_tokens` ≤ 800 (writing) / 400 (router).
- Images → `POST https://api.x.ai/v1/images/generations`, model
  `grok-imagine-image`, **behind `authMiddleware`**.
- Degrade: if the key is missing, show a calm empty state — never crash.

Persist per-user results with **`neon`** + `authMiddleware` (`user_id` text).

---

## 4. Design language (iOS, not “AI slop”)

This is **iOS grouped** — light, hairline, large titles — not purple glow soup.

- Background `#F2F2F7`, surfaces `#FFFFFF`, label `#1C1C1E`, secondary `#8E8E93`
- **One accent:** iOS system blue `#0A84FF` (this is authentic, not a slop purple)
- Type: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", system-ui`
- Grouped lists, large titles, bottom tab bar (≤5) on ~390px; iPad-style
  sidebar from `md` up
- Concentric radii: cards ~14–16, inner controls 10–12
- **Intelligence mark only on the orb / thinking state** — a small iridescent
  conic gradient (sky / rose / pale gold). Never wash the whole page in it.
- No emoji in chrome. Lucide icons, 1.75 stroke, optically SF-like.

Tokens live in `src/styles.css` `@theme`. See **`design-ui`**.

---

## 5. Native Swift (reference only)

When the user wants “real” Apple Intelligence, put a **reference panel** in
the app (copyable Swift) and keep the live demo on the web path.

Minimum set to mention (iOS 26 / 27, Xcode 27 — see `references/native-apis.md`):

- `import FoundationModels` → `SystemLanguageModel`, `LanguageModelSession`,
  `@Generable` / `@Guide`, `Tool`, multimodal `Attachment`
- `PrivateCloudComputeLanguageModel` + `reasoningLevel` for heavier work
- `LanguageModel` protocol for third-party / Grok-class providers
- `AppIntents` schemas so Siri AI can run *your* actions
- `ImagePlayground` (incl. photorealistic / `ImagePlaygroundStyle.all` on PCC)

Do **not** add a fake Xcode project to `/workspace`. It cannot build here.

---

## 6. Finish checklist

- [ ] Viewport `viewport-fit=cover` + safe-area padding on shell / tab bar
- [ ] Apple web-app meta + theme-color match the grouped background
- [ ] Native `textarea` / inputs at 16px; context menu not blocked
- [ ] Share Sheet wired on every result
- [ ] Writing Tools, Image Playground, Visual Intelligence, Intents are
      **playable**, not documented-only
- [ ] xAI calls user-initiated, capped; images auth-gated; missing-key empty state
- [ ] Per-user library scoped by `authMiddleware`
- [ ] German (or locale) copy uses Apple’s verbs
- [ ] Fallback vs. on-device is labeled — no false “on-device” claim
- [ ] Mobile 390px: no overflow, 44px targets, tab bar clear of home indicator
- [ ] Skill registered in `AGENTS.md` skills table if you added this folder
