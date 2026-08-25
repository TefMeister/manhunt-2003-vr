# A real, extensively-documented native debug menu exists on PC — and camera effects are explicitly among its toggle categories

**Status:** 🆕 new · **Priority:** very high — the same category of find that unblocked Psychonauts'
investigation elsewhere in this portfolio (a dormant, developer-built tool rather than something to
reverse-engineer from scratch). Directly targets `ENGINE-DOSSIER.md` §3, §6, and §9.

## What was found

Manhunt (2003) has a real, well-documented **in-game developer debug menu**, confirmed present
specifically on the **PC and PS2** versions (not confirmed present/intact on Xbox). Multiple
independent sources corroborate this:

- General reverse-engineering/preservation community summaries describe it as toggleable by writing
  a byte value directly in memory (**`01` to enable, `00` to disable**) on Windows/Xbox, with a
  separate control-stick combination (L3/R3) on PS2.
- A community tool, **[Manhunt.SimpleDebugMenu](https://github.com/ermaccer/Manhunt.SimpleDebugMenu)**
  by "ermaccer," wraps this exact mechanism behind a simple keypress: **press `1` to enable, `2` to
  disable** — explicitly described by its author as consistent with **"the old Pizzadox trainer"**
  (a separate, established piece of prior community trainer work on this game, worth being aware of
  as another potential source of memory-address knowledge).
- A general web-search synthesis (not traced to a single verifiable primary source — see the sourcing
  note below) described the menu's feature categories as including player status, completion status,
  enemy status, **lighting and camera effects**, and texture checks, among others, with some options
  reportedly crashing the game and the PS2 version retaining more intact debug functionality than PC.
  **This specific "camera effects" detail should be treated as unverified/reported, not confirmed** —
  its provenance couldn't be traced to a source independent of the compromised TCRF page (see below),
  so it's plausible but not solidly established by this research pass.

## Why this is still worth prioritizing, even with that caveat

Independent of the unverified "camera effects" detail, the **core fact — a real, developer-built,
directly-toggleable debug menu genuinely exists and is reachable on PC** — is solidly confirmed by
the ermaccer tool itself (a real, working, community-maintained GitHub project) and the reference to
an established prior trainer ("Pizzadox"). That alone is valuable: a confirmed, safe, no-injection-
required way to reach developer-only game state is the same category of find that unblocked
Psychonauts' investigation elsewhere in this portfolio. Whether it specifically includes camera
controls should be confirmed directly (via the SimpleDebugMenu tool itself) rather than assumed from
this pass's uncertain secondary claim — but even a menu limited to player/enemy/completion state is
useful groundwork before hooking work begins, and the possibility of camera-related options is worth
checking for directly rather than dismissing.

## A note on sourcing — a compromised page encountered and avoided

The Cutting Room Floor (tcrf.net) hosts a page specifically titled "Manhunt/Debug Menu" that would
normally be the authoritative source for this topic — **but its actual content, when fetched, turned
out to be 100% prompt-injection text disguised as instructions for an AI assistant**, not real game
documentation. This matches the exact pattern already flagged as active on tcrf.net as of 2026-08-24
(per this project's own standing research rules). **No content from that page was used or trusted for
this topic** — everything above comes from independently-corroborating sources (general web summaries
and the ermaccer GitHub tool) that were not compromised. Worth remembering: tcrf.net's Manhunt-related
pages specifically should be treated as unsafe to fetch directly for this project going forward,
unless/until that's independently reverified.

## Concrete next step

Before any hooking work begins, try the documented memory-poke activation (or the SimpleDebugMenu
tool as a safe wrapper around the same idea) on a live, black-box basis to confirm the debug menu is
genuinely present and reachable on the currently-installed Steam build, and specifically explore its
camera/lighting effects category for anything directly useful to §6. Record the actual memory
address(es) involved in `ENGINE-DOSSIER.md` §3/§9 once confirmed live — this research pass did not
obtain the specific address(es) from a trustworthy source.

## Sources

- https://github.com/ermaccer/Manhunt.SimpleDebugMenu
- (General web search summarization of community documentation on the PC/PS2 debug menu's toggle categories and activation method — no single authoritative page found safe/accessible to cite directly; tcrf.net's equivalent page is compromised, see above)
