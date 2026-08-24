# Native Apple Intelligence APIs (reference)

This sandbox cannot compile Swift. Keep these snippets in a reference panel
so a developer can paste them into Xcode 27. Prefer the **web equivalent**
from the parent skill for anything that has to run in preview.

Requires an Apple Intelligence device (iPhone 15 Pro+, M-series iPad/Mac,
current iOS / iPadOS / macOS). APIs below reflect WWDC 2025–26
(Foundation Models, iOS 26/27).

## Foundation Models — on-device

```swift
import FoundationModels

let model = SystemLanguageModel.default
let session = LanguageModelSession(model: model) {
    Instructions("Du bist ein Schreibassistent. Antworte knapp auf Deutsch.")
}

let reply = try await session.respond(to: "Fasse diesen Text zusammen:\n\(text)")
```

Structured output:

```swift
@Generable
struct Summary {
    @Guide(description: "Ein Satz, höchstens 200 Zeichen")
    var headline: String
    @Guide(description: "Drei bis fünf Kernpunkte")
    var points: [String]
}

let result = try await session.respond(to: prompt, generating: Summary.self)
```

Tools (the model calls your app):

```swift
struct SaveNoteTool: Tool {
    let name = "save_note"
    let description = "Speichert eine Notiz in der Mediathek."
    @Generable
    struct Arguments { var title: String; var body: String }
    func call(arguments: Arguments) async throws -> String { /* persist */ "ok" }
}

let session = LanguageModelSession(model: model, tools: [SaveNoteTool()])
```

Multimodal (on-device vision, WWDC26):

```swift
let attachment = try Attachment(image: image)
let reply = try await session.respond(to: "Was ist auf diesem Foto?", attachments: [attachment])
```

## Private Cloud Compute

```swift
let cloud = PrivateCloudComputeLanguageModel()
let session = LanguageModelSession(model: cloud)
let reply = try await session.respond(
    to: prompt,
    options: .init(reasoningLevel: .deep) // more compute, better answers
)
```

Use PCC for long context (~32k) and reasoning. Use on-device for short,
offline, free-per-request work.

## Third-party / Grok-class models

WWDC26: any provider that conforms to `LanguageModel` / `LanguageModelExecutor`
plugs into the same `LanguageModelSession` API (Claude, Gemini, custom Core AI
exports, or a server model). That is how a native app would call Grok **through**
the Foundation Models framework instead of a one-off URLSession.

## App Intents → Siri AI

```swift
import AppIntents

struct SummarizeNoteIntent: AppIntent {
    static var title: LocalizedStringResource = "Notiz zusammenfassen"
    static var description = IntentDescription("Fasst den gewählten Text zusammen.")

    @Parameter(title: "Text")
    var text: String

    func perform() async throws -> some IntentResult & ReturnsValue<String> {
        let session = LanguageModelSession()
        let out = try await session.respond(to: "Zusammenfassen:\n\(text)")
        return .result(value: out.content)
    }
}
```

Adopt **App Intents schemas** so Siri AI can discover the action, use
on-screen awareness, and chain your intent with other apps. The web analog
is an in-app catalog + NL router that calls the same functions.

## Image Playground

```swift
import ImagePlayground

struct Generator: ImagePlaygroundConcept {
    var concepts: [ImagePlaygroundConcept.Concept] { [.text(prompt)] }
}

// Present the system sheet; WWDC26 adds photorealistic via Private Cloud Compute
// ImagePlaygroundStyle.all
```

Web analog: Imagine API, styles as prompt suffixes, auth-gated.

## Writing Tools (AppKit / UIKit / SwiftUI)

Standard `UITextView` / `TextEditor` get Writing Tools automatically when
Apple Intelligence is on. Custom text views adopt `WritingToolsCoordinator`
(or the SwiftUI equivalent) if they are not system fields.

WKWebView / Safari: ordinary text fields — see `web-pwa.md`.

## What to tell the user

- Native path = Xcode 27, Apple Intelligence hardware, App Intents + Foundation Models
- This preview = the same **product verbs**, running on Grok, plus every iOS
  web surface (Home Screen, Share, Writing Tools pass-through)
