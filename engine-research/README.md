# Manhunt (2003) — VR Engine Research

Engine research toward a VR conversion of **Manhunt** (2003) — built on the
**RenderWare** engine (licensed from Criterion Software) by Rockstar North,
published by Rockstar Games — with stereo rendering and 6DOF head tracking as
the goal.

This folder holds two things:

- **[`PLAYBOOK.md`](PLAYBOOK.md)** — a reusable, engine-agnostic, point-by-point
  method for taking *any* game whose engine nobody has converted to VR and
  getting it there. It is oriented around one North Star: **the game rendering
  in a headset with head tracking**, with everything else built on top. The same
  playbook is copied into each of our VR projects' research repos.
- **[`ENGINE-DOSSIER.md`](ENGINE-DOSSIER.md)** — the distilled, current-truth
  reference for *this* game's engine. Only the identity section is filled in
  so far — engine research has not started yet; this repo was seeded ahead of
  that work so the project structure is ready.

The blow-by-blow development history will live in the sibling folders
(`-dev-archive` for the messy in-progress record, `-modding-notes` for readable
field notes). This repo is the consolidated engine knowledge, not the diary.

## The folders for Manhunt VR

Everything for this game lives in one repository, one folder per job — so you
always know where to look. You are in **`engine-research/`**.

| Folder | What lives here |
| --- | --- |
| [`mod/`](../mod/) | The mod itself — once code exists, it lands here. |
| [`dev-archive/`](../dev-archive/) | Full development history — snapshots, probes, dead ends, raw recon. |
| [`modding-notes/`](../modding-notes/) | Readable field notes / progress ledger. |
| [staging/manhunt-2003-vr](https://github.com/TefMeister/staging/tree/main/manhunt-2003-vr) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| **`engine-research/`** ← you are here | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [`external-research/`](../external-research/) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Status

Project started 2026-08-25. Groundwork phase: repos just created, no
reverse-engineering has begun yet. See the dossier for the current phase and
open risks as they're identified.

## Scope, ethics, and legality

- This is a **non-commercial fan project**. It requires owning a legitimate copy
  of the game and **redistributes no original game assets** — only files we
  create. See [`.gitignore`](.gitignore).
- We **credit everyone** whose work or research this builds on, and we honour
  correction/removal requests from actual rights holders. See
  [`CREDITS.md`](CREDITS.md).

## Templates

New engine? Start its dossier from
[`templates/per-engine-research-template.md`](templates/per-engine-research-template.md).

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
