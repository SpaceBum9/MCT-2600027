export function isIosDevice(): boolean {
  if (typeof navigator === "undefined") return false;
  return (
    /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1)
  );
}

export function isStandaloneDisplay(): boolean {
  if (typeof window === "undefined") return false;
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    Boolean((navigator as Navigator & { standalone?: boolean }).standalone)
  );
}

export function canShare(): boolean {
  return typeof navigator !== "undefined" && typeof navigator.share === "function";
}

export function canClipboard(): boolean {
  return typeof navigator !== "undefined" && Boolean(navigator.clipboard?.writeText);
}

export async function shareOrCopy(payload: {
  title: string;
  text: string;
  url?: string;
}): Promise<"shared" | "copied" | "failed"> {
  if (canShare()) {
    try {
      await navigator.share(payload);
      return "shared";
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") return "failed";
    }
  }
  if (canClipboard()) {
    try {
      await navigator.clipboard.writeText(payload.text);
      return "copied";
    } catch {
      return "failed";
    }
  }
  return "failed";
}

export function writingToolsLikely(): boolean {
  return isIosDevice();
}
