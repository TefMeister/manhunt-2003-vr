# 2026-08-25 — First live test: two real, separate obstacles hit

## What happened, in plain terms

This was also the first try at a new way of working together: you launch the game whenever
you get a free moment, and I take over from there rather than needing you to stay and test
things live. First real run of that, and it surfaced two genuinely separate problems.

**Problem one — the community-documented fix for this game's known bug turned out to be
broken on our copy.** Manhunt's Steam release has a well-known issue: leftover anti-piracy
checks that were never fully removed, which misfire now that the actual protection is gone,
causing doors not to open, AI to misbehave, and memory leaks. The standard fix swaps in a
second file (`testapp.exe`) that Rockstar's Steam packaging already includes for exactly this
purpose. We tried it — it crashed the game outright, instantly, both times. Digging into it
technically, that specific file's own internal "where do I start running" pointer is broken,
pointing at the wrong part of itself. Not something we caused; that file is just bad on this
particular install. We put the original file back.

**Problem two — the original game launches, but hits exactly the known bug.** With the
original file restored, the game got past the video-settings screen (no windowed-mode option
there, unfortunately — fullscreen only) and into an actual level, but immediately hit the
documented bug: a gate that's supposed to open for an enemy character stayed shut, blocking
you from continuing. After sitting stuck there a few minutes, the game itself stopped
responding entirely and had to be force-closed — again, a known side effect of this same bug
(it's documented to cause memory leaks), not something new.

**Along the way**, tried connecting a live debugger to inspect the running game more closely
— that got blocked, the same kind of block we saw once before on Mad Max's copy-protected
build, even though Manhunt isn't supposed to have that kind of protection. Likely just a
lighter-weight Steam wrapper, but it means live debugger work needs its own separate
investigation before it'll work here.

**Also tried**: found and read (without downloading anything, just viewing a public GitHub
page) a community tool that's supposed to properly fix this exact bug by patching the game's
memory at 16 specific spots. Understood exactly how it works — but the specific memory
locations it lists don't match up on our exact copy of the game (checked carefully, the math
was right, the bytes just weren't what was expected). Games get updated over the years and
those locations shift, so this needs to be re-discovered for our specific copy rather than
reused as-is.

## Where things stand

Nothing is fixed yet, but everything's understood and none of it is a mystery: two separate,
well-documented problems, both explained, both with a clear path forward. The proxy tool we
built for watching this game's rendering calls did load correctly in both test runs — that
part's working fine, it just never got far enough to matter yet because of the gate bug.

## What's next

The remaining work — figuring out the correct memory addresses for this exact copy of the
game — is desk work that doesn't need the game running at all, so that'll happen in the
background. Next time you've got a free moment to launch it again, it'll be to test whatever
comes out of that.

Full technical detail: `manhunt-2003-vr-engine-research`, `ENGINE-DOSSIER.md` §4/§11.
