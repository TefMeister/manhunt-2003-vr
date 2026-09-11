# The 0x00431820 restart/save crash — our own site-#1 patch (2026-09-11)

Distilled: dossier §11l. Reader analyses: `reader-analysis.md` (the cause),
`reader-entitydata-write-and-read.md` (the fix), `reader-play-continue-and-save-repair.md` (why
PLAY continued a save, and the offline repair).

| File | What it shows |
| --- | --- |
| `crash-excerpt.txt` + the `manhunt_crash_*.bin` dumps | Tefa's 16:27 crash: `0x00431820`, "No archetype of this name exists : d". |
| `log-13-load-tefa-save-crash-00431820-reproduced.txt` | Loading her 16:39 save reproduces it. |
| `log-14-load-tefa-save-tocsize-OFF-still-crashes.txt` | Same with TOCSIZE disabled — TOCSIZE ruled out. |
| `log-15-august-save-loads-fine.txt` | The August save (empty snapshot) loads fine. |
| `log-16-site1-stock-FRESH-new-game-crashes.txt` | ⚠️ Looked like "stock crashes a fresh start" — **it was not fresh**: PLAY had continued her save (`DRMLOG #1 eax` is a heap pointer). |
| `log-17-site1-PATCHED-play-also-crashes.txt` | The same PLAY with the patch on also crashes — the clue that PLAY was continuing her save. |
| `log-19-entityfix-repairs-tefa-save-execution-swap-restart-ok.txt` | Build `fa8d777d` + `manhunt_vr_fix_entitydata`: her save repaired and loaded; a stealth execution; an item swap; die → Continue with no crash. |
| `log-20-entityfix-fresh-new-game-from-disk-ok.txt` | A true fresh start (`eax=0x00000001`), no crash. |
| `log-21-offline-repaired-save-loads-clean.txt` | The one-byte offline repair loads with nothing to repair. |
| `ef-01.png`, `efseq-06.png` | Her save selected, then loaded after the repair. |
| `stalk-10.png`, `stalk-11-exec.png` | The execution lock-on behind hBackAlley, then the camcorder kill scene. |
| `swap.png` | Item swap: shard for bag, no crash. |
| `cont-05.png` | Back at the save point after "Scene Failed!" → Continue. |
| `repaired-save-loaded.png` | The offline-repaired save, loaded. |
