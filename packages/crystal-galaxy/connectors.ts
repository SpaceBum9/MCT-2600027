import { GITHUB_REPOS, GH_OWNER, HF_OWNER } from "./catalog";

export const HF_IMPORT = {
  owner: HF_OWNER,
  space: "kreuzkopplung",
  sourceRepo: `${GH_OWNER}/kreuzkopplung`,
  sdk: "gradio",
  appFile: "app.py",
  files: [
    "app.py",
    "dual_entangled.py",
    "requirements.txt",
    "README.md",
    "LICENSE",
  ],
  spaceUrl: `https://huggingface.co/spaces/${HF_OWNER}/kreuzkopplung`,
  githubUrl: `https://github.com/${GH_OWNER}/kreuzkopplung`,
  createUrl: "https://huggingface.co/new-space",
  apiUrl: `https://huggingface.co/api/spaces/${HF_OWNER}/kreuzkopplung`,
} as const;

export const GH_PULSE_REPOS = GITHUB_REPOS.map(
  (name) => `${GH_OWNER}/${name}` as const,
);

export const DRIVE_ANCHORS = [
  {
    id: "automat-orchestrieren",
    title: "Automat Orchestrieren",
    href: "https://docs.google.com/document/d/1HoJ07dgtlxOWBnpB3dl11p9AcFADSa5dlW5w8VfDrnA/edit",
    role: "Control Plane · Schema · Mesh",
  },
  {
    id: "kernel-status",
    title: "Crystal Galaxy Kernel Status",
    href: "https://docs.google.com/document/d/1RwX-s8YOlTTTz28XUDYzQAJyBiRinnLjBn7u7lV7-0A/edit",
    role: "Täglicher Kernel-Anker",
  },
  {
    id: "kernel-ausbau",
    title: "Kernel Ausbau 2026-08-19",
    href: "https://docs.google.com/document/d/1nu_64gRvT57n0nxN_PDa3wwqu9zkgzZUVkt2Ad6ba1s/edit",
    role: "Ausbau-Log",
  },
] as const;

export type RepoPulse = {
  fullName: string;
  description: string | null;
  language: string | null;
  pushedAt: string | null;
  htmlUrl: string;
  private: boolean;
  ok: boolean;
};

export type HfPulse = {
  exists: boolean;
  id: string | null;
  runtime: string | null;
  sdk: string | null;
  likes: number | null;
  url: string;
};

export type ConnectorPulse = {
  fetchedAt: string;
  github: RepoPulse[];
  huggingface: HfPulse;
};
