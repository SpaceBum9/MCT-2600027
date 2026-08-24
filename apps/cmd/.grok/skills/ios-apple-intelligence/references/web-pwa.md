# iOS web / PWA contract

Use this when wiring any app that should feel installed on iPhone / iPad.

## Meta (root `head`)

```ts
{ name: "viewport", content: "width=device-width, initial-scale=1, viewport-fit=cover" }
{ name: "theme-color", content: "#F2F2F7" }
{ name: "apple-mobile-web-app-capable", content: "yes" }
{ name: "mobile-web-app-capable", content: "yes" }
{ name: "apple-mobile-web-app-title", content: APP_NAME }
{ name: "apple-mobile-web-app-status-bar-style", content: "default" }
{ name: "format-detection", content: "telephone=no" }
```

Keep the template’s Grok PWA manifest + `apple-touch-icon`. Do not invent a
second manifest. Do not delete `public/__grok/`.

## Safe area

```css
.shell {
  padding-top: env(safe-area-inset-top);
  padding-bottom: calc(env(safe-area-inset-bottom) + var(--tabbar-h, 52px));
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}
```

Fixed tab bars add `padding-bottom: env(safe-area-inset-bottom)` on the bar
itself. Large titles scroll under the status bar — the nav stays padded.

## Standalone vs. Safari

```ts
export function isIos(): boolean {
  if (typeof navigator === "undefined") return false;
  return /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
}

export function isStandalone(): boolean {
  if (typeof window === "undefined") return false;
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    Boolean((navigator as Navigator & { standalone?: boolean }).standalone)
  );
}
```

Show “Zum Home-Bildschirm” only when `isIos() && !isStandalone()`. Point at
the platform install page (`?install=1&platform=ios`) rather than inventing
a second tutorial.

## Writing Tools (Safari / WKWebView, iOS 18.1+)

Apple Intelligence Writing Tools attach to **selected text** in:

- `<textarea>` and `<input type="text">`
- `contenteditable="true"` (true, not `plaintext-only` if you want full tools)
- `WKWebView` with default text interaction

**Do**

- Use a real form control
- Allow selection and the system callout
- Keep font-size ≥ 16px

**Don’t**

- `user-select: none` on the field
- `preventDefault()` on `contextmenu` / `selectstart`
- Capture every `keydown` for a custom editor
- Replace the field with a `canvas` or a contenteditable that owns `beforeinput`

You may *also* offer the same verbs as in-app buttons (Umschreiben, …). Those
run via xAI so desktop / Android / the Grok preview still work. On a real
iPhone both paths coexist.

## Share, clipboard, speech

```ts
async function shareOrCopy(payload: { title: string; text: string; url?: string }) {
  if (navigator.share) {
    try { await navigator.share(payload); return; } catch { /* user cancel */ }
  }
  await navigator.clipboard.writeText(payload.text);
}
```

`Web Speech API` (`SpeechRecognition` / `webkitSpeechRecognition`) is the
Siri-adjacent mic for in-app dictation. It is **not** Siri. Label it “Diktat”.

## Input hygiene

| Rule | Why |
| --- | --- |
| `font-size: 16px` on inputs | Stops Safari zoom-on-focus |
| `autocomplete` / `enterKeyHint` set | iOS keyboard is part of the UI |
| `inputMode="text"` / `search` as needed | Correct keyboard |
| 44px min hit target | HIG |
| `overscroll-behavior: none` on the app shell | Stops rubber-band revealing white |
| `-webkit-tap-highlight-color: transparent` | Then provide your own pressed state |

## What the web cannot do

- On-device Foundation Models
- Real App Intents / Siri AI schemas
- Image Playground system sheet
- Visual Intelligence camera button in Control Center
- Private Cloud Compute
- Genmoji / Image Wand / Clean Up

Document these. Implement the **verb** with xAI. Never claim “on-device”.
