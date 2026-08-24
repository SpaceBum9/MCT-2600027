export const WRITING_MODES = [
  {
    id: "rewrite",
    label: "Umschreiben",
    hint: "Klarer, ohne den Sinn zu verdrehen",
    instruction:
      "Schreibe den Text um. Behalte Sprache, Fakten und Länge ungefähr bei. Keine Einleitung, nur der neue Text.",
  },
  {
    id: "proofread",
    label: "Korrektur",
    hint: "Rechtschreibung, Grammatik, Zeichensetzung",
    instruction:
      "Korrigiere Rechtschreibung, Grammatik und Zeichensetzung. Ändere den Stil nicht. Gib nur den korrigierten Text zurück. Wenn nichts zu ändern ist, gib den Originaltext unverändert zurück.",
  },
  {
    id: "summarize",
    label: "Zusammenfassen",
    hint: "Ein knapper Absatz",
    instruction:
      "Fasse den Text in 3–6 Sätzen zusammen. Keine Aufzählung, keine Überschrift.",
  },
  {
    id: "keypoints",
    label: "Kernpunkte",
    hint: "Die wichtigsten Aussagen",
    instruction:
      "Extrahiere 4–7 Kernpunkte als Markdown-Liste mit Bindestrichen. Kein Fließtext davor oder danach.",
  },
  {
    id: "list",
    label: "Liste",
    hint: "Als Aufzählung",
    instruction:
      "Wandle den Inhalt in eine klare Markdown-Liste um. Gruppiere sinnvoll. Nur die Liste.",
  },
  {
    id: "table",
    label: "Tabelle",
    hint: "Als Markdown-Tabelle",
    instruction:
      "Strukturiere den Inhalt als Markdown-Tabelle mit Kopfzeile. Nur die Tabelle.",
  },
  {
    id: "friendly",
    label: "Freundlich",
    hint: "Wärmer, näher",
    instruction:
      "Schreibe den Text freundlicher und zugänglicher um. Behalte die Aussage. Nur der neue Text.",
  },
  {
    id: "professional",
    label: "Professionell",
    hint: "Ruhig, präzise",
    instruction:
      "Schreibe den Text professionell und knapp um. Kein Marketing-Sprech. Nur der neue Text.",
  },
  {
    id: "concise",
    label: "Prägnant",
    hint: "Kürzer, gleiche Aussage",
    instruction:
      "Kürze den Text deutlich, ohne Fakten zu streichen. Nur der neue Text.",
  },
  {
    id: "compose",
    label: "Verfassen",
    hint: "Aus einer kurzen Vorgabe",
    instruction:
      "Verfasse aus der Vorgabe einen fertigen, natürlichen Text auf Deutsch. Keine Meta-Kommentare.",
  },
] as const;

export type WritingModeId = (typeof WRITING_MODES)[number]["id"];

export const IMAGE_STYLES = [
  {
    id: "illustration",
    label: "Illustration",
    suffix:
      "Flat editorial illustration, soft daylight, clean shapes, restrained palette of pale stone, ink, and sky blue, no text, no watermark.",
  },
  {
    id: "animation",
    label: "Animation",
    suffix:
      "Soft 3D animation still, rounded forms, gentle studio light, premium toy-like finish, no text.",
  },
  {
    id: "sketch",
    label: "Skizze",
    suffix:
      "Refined pencil and wash sketch on warm paper, confident line, no text.",
  },
  {
    id: "photo",
    label: "Foto",
    suffix:
      "Photorealistic photograph, natural light, shallow depth of field, no text, no watermark, no logo.",
  },
] as const;

export type ImageStyleId = (typeof IMAGE_STYLES)[number]["id"];

export const APP_INTENTS = [
  {
    id: "composeWriting",
    title: "Text verfassen",
    phrase: "Verfasse eine Nachricht",
    destination: "/write",
    schema: "Create.Draft",
    description: "Öffnet die Schreibwerkzeuge mit einer Vorgabe.",
  },
  {
    id: "rewriteText",
    title: "Text umschreiben",
    phrase: "Schreibe das um",
    destination: "/write",
    schema: "Update.Content",
    description: "Reicht markierten Text an Umschreiben weiter.",
  },
  {
    id: "summarize",
    title: "Zusammenfassen",
    phrase: "Fasse das zusammen",
    destination: "/write",
    schema: "Create.Summary",
    description: "Erzeugt eine Kurzfassung des aktuellen Texts.",
  },
  {
    id: "generateImage",
    title: "Bild erzeugen",
    phrase: "Erstelle ein Bild von …",
    destination: "/images",
    schema: "Create.Image",
    description: "Startet Image Playground mit einem Motiv.",
  },
  {
    id: "inspectImage",
    title: "Bild verstehen",
    phrase: "Was ist auf diesem Foto?",
    destination: "/vision",
    schema: "Inspect.Image",
    description: "Visual Intelligence: beschreibt ein Foto.",
  },
  {
    id: "openLibrary",
    title: "Mediathek öffnen",
    phrase: "Zeig meine gespeicherten Texte",
    destination: "/library",
    schema: "Open.Collection",
    description: "Öffnet gespeicherte Ergebnisse.",
  },
  {
    id: "installIos",
    title: "Aufs iPhone legen",
    phrase: "Installiere Lumen",
    destination: "/ios",
    schema: "Open.Settings",
    description: "Zeigt die iOS-Eingliederung und den Home-Screen-Weg.",
  },
] as const;

export type AppIntentId = (typeof APP_INTENTS)[number]["id"];
