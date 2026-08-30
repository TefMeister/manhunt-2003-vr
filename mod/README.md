# Manhunt VR

A VR conversion mod for **Manhunt** (2003) — the goal is stereo rendering and
6DOF head tracking, built on the game's **RenderWare** engine foundation.

> **Status: work in progress — nothing playable released yet, no code written
> yet.** This repository will hold releases only; watch it if you want to know
> the moment there is something to try.

## What this will be

Manhunt (2003) runs on RenderWare (Criterion Software's licensed engine,
the same generation used across several early-2000s titles), so this project
starts from the general shape of a RenderWare VR conversion: locate the
camera/projection delivery, get stereo rendering with a per-eye view offset,
then layer head tracking on top. Nothing has been reverse-engineered yet —
this repository was created to get the project structure in place before that
work begins. The real goal, as with all of our projects, is the knowledge
gained on the way there, written down and shared so anyone can do the same
for any game — see the
[engine dossier](https://github.com/TefMeister/manhunt-2003-vr-engine-research)
and the cross-engine
[flat-to-VR library](https://github.com/TefMeister/flat-to-vr-cross-engine-research).

## What you will need

- Your own legitimate copy of **Manhunt** (2003) (this mod contains **no**
  game files).
- A PC VR headset (target runtime to be decided — SteamVR/OpenXR, in line with
  our other projects).

## The six repositories for Manhunt VR

Everything for this game lives in six repositories, each with one job — so you
always know where to look. You are in **manhunt-2003-vr-mod**.

| Repository | What lives here |
| --- | --- |
| **manhunt-2003-vr-mod** ← you are here | The mod itself — once code exists, it lands here. |
| [manhunt-2003-vr-dev-archive](https://github.com/TefMeister/manhunt-2003-vr-dev-archive) | Full development history — snapshots, probes, dead ends, raw recon. |
| [manhunt-2003-vr-modding-notes](https://github.com/TefMeister/manhunt-2003-vr-modding-notes) | Readable field notes / progress ledger. |
| [manhunt-2003-vr-staging](https://github.com/TefMeister/manhunt-2003-vr-staging) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| [manhunt-2003-vr-engine-research](https://github.com/TefMeister/manhunt-2003-vr-engine-research) | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [manhunt-2003-vr-external-research](https://github.com/TefMeister/manhunt-2003-vr-external-research) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Credits, scope, and legality

Non-commercial fan project; requires an owned copy; redistributes no original
assets. We credit everyone whose work this builds on — see
[`CREDITS.md`](CREDITS.md) — and we honour correction/removal requests from
rights holders promptly.

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
