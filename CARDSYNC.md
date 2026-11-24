# cardsync -- spec rev 3 (2026-11-24)

**Status: implemented** (`scripts/cardsync.py`, rev 2 approved by the user
2026-11-24, "cardsync queda aprobado: adelante"). Rev 3 records how the
build settled what rev 2 left open (section 10).

Host script that keeps a project's MSX tree in step with the Nextor SD card.
Rev 0 was approved on 2026-11-03 but never written to disk; this revision
rebuilds it from the recorded decisions (`.memory/project_sxdev.md`, SXDEV
README "Moving work between the MSX and the repository") and adds the
details needed to build it. Rev 2: the card layout of WRECK (WORK\DEV\WRECK,
makefile at the root, code in SRC), now that M80 2.00 takes paths (SXDEV E47).

## 1. Principles (from rev 0)

- The repository is the truth; the card is a working copy, never the only copy.
- A dated backup of the card directory before anything is written to it.
- Only MSX paths: 8.3 names. Anything else is never copied, and is reported.
- Change detection by **content hash against the last sync**, never dates and
  never the FAT archive bit (that bit belongs to SMAKE).
- A file changed on both sides since the last sync is a **conflict**: stop,
  touch nothing, say which files.
- Never a git commit, add or stash. cardsync moves files; the user commits.
- The project directory holds the makefiles, `.BAT`, `.LNK` and `.TXT`; the
  code goes in `SRC`, the assets in `GFX`, `MAP`, `MUS`: sub-directories one
  level deep (rev 1 had the card flat; M80/L80 2.00 and every SXDEV tool take
  paths).

## 2. Configuration: `cardsync.cfg`

One file at the root of the host project, one mapping per file:

```
[card]
volume  = WORK            ; /Volumes/WORK (B: on the MSX)
dir     = DEV\WRECK       ; card directory, 8.3 items, created by init
[local]
dir     = MSX             ; host directory mirrored, relative to the cfg
subdirs = SRC GFX MAP MUS ; the only sub-directories synced (one level)
ignore  = *.REL *.LST *.PRN *.SYM *.CRF *.$$$ *.BAK
```

`ignore` patterns (fnmatch, upper case) are never copied either way: build
products made on the MSX stay on the MSX. A file the user wants back (a
built `.ROM`) is simply not ignored.

## 3. Commands

```
cardsync [-n] [--eject] init      create the card dir + subdirs, first sync
cardsync status                   what pull/push would do, conflicts, refused names
cardsync [-n] [--delete] pull     card -> host
cardsync [-n] [--delete] push     host -> card
cardsync resolve FILE card|local  settle one conflict by choosing a side
```

- `-n` dry run: print the plan, write nothing (no backup either).
- `--eject` after a successful run: `diskutil eject` of the whole disk
  (takes every partition of the card together).
- `init`: card dir absent or empty -> create it and push everything; host
  dir empty -> pull everything; both non-empty -> refuse unless every common
  file is byte-equal (then it just records the state).
- The cfg is found in the current directory or its parents (like git).

## 4. Sync rules

State `.cardsync/state.json` (beside the cfg, excluded from git): for each
synced path, the SHA-256 recorded at the last sync. For each path P seen on
either side, with `L` = local hash, `C` = card hash, `S` = state hash:

| L vs S | C vs S | pull | push |
|--------|--------|------|------|
| same | same | nothing | nothing |
| same | changed | copy card -> host | report "newer on card", copy nothing |
| changed | same | report "newer on host" | copy host -> card |
| changed | changed, L != C | **conflict** | **conflict** |
| changed | changed, L == C | record state | record state |
| absent from state, one side only | | new: copy | new: copy |
| absent from state, both, equal | | record | record |
| absent from state, both, differ | | **conflict** | **conflict** |
| deleted on one side, other unchanged | | reported; removed only with `--delete` | same |
| deleted on one side, other changed | | conflict | conflict |

Any conflict -> the whole run writes nothing (exit 1). `status` lists them;
`resolve` copies the chosen side over the other and records the state.

A one-way command never overwrites the newer side: `push` never touches a
file only the card changed, `pull` never one only the host changed.

## 5. Names

Synced: `NAME.EXT` matching `[A-Z0-9_$#%&!-]{1,8}(\.[A-Z0-9_$#%&!-]{1,3})?`,
in the dir itself or in a listed sub-dir. Lower-case or long names are
refused with a warning, never renamed. Always ignored silently: `._*`,
`.DS_Store`, `.Trashes`, `.Spotlight-V100`, `.fseventsd`,
`System Volume Information`. Unlisted sub-directories are reported, not
entered.

## 6. Writing

- Card not mounted, or `diskutil info` does not report MS-DOS FAT -> exit 3,
  nothing done.
- Before the first write to the card: copy the whole card dir to
  `.cardsync/backup/YYYYMMDD-HHMMSS/` (the last 10 kept). A host file about to
  be overwritten or deleted by `pull` goes to the same backup under `HOST/`.
- Copy with `COPYFILE_DISABLE=1`, no extended attributes, mtime preserved;
  delete any `._*` the copy left; `sync`; then **read every written file
  back and compare** -- a mismatch stops with exit 4 and leaves the state
  unchanged.
- Bytes are never converted (CR LF stays CR LF; the repo stores the MSX
  files as they are -- `.gitattributes`: `MSX/** -text`).
- The state is written last, only after every read-back passed.

## 7. Exit codes

0 done / nothing to do, 1 conflicts or pending changes reported by `status`,
2 usage or cfg error, 3 card not mounted / not FAT, 4 read-back mismatch.

## 8. Place and tests

`msxtools/scripts/cardsync.py` (Python 3, standard library only), wrapper
installed by `install_wrappers.sh`. `CARDSYNC_ROOT` overrides `/Volumes`
and skips the FAT check, for the tests.
`msxtools/scripts/test_cardsync.py` (unittest): a fake card in a temp dir,
one case per row of the table in 4, names, ignore, backup, read-back
failure (injected), dry run writes nothing; plus a mutation list proving
each case fails when its rule is broken.

## 9. Open

- The SXDEV tools on the card (`B:\SXDEV`, on the PATH since 2026-11-10,
  copied by hand): a second cfg in SXDEV mapping `BUILD/*.COM` one way (push
  only), or out of scope.

## 10. Settled by the build (rev 3)

- **One way means one way**: `push` copies host -> card only, `pull` card ->
  host only. "new: copy" in 4 is in the command's direction; a file new,
  changed or deleted on the other side is reported ("... not touched by
  push") and left for the other command. `--delete` removes on the target
  side only what the source side deleted.
- **No state yet** (a project first synced by hand, as WRECK): every path is
  "absent from state": equal on both sides -> recorded by the next `push` or
  `pull`, different -> conflict. `init` is only needed for an empty side.
- `status` checks the card too (exit 3 when it is not mounted): without it
  every host file would read "new on host". It writes nothing, the state
  neither.
- Records (`equal, not recorded yet`) are not pending: `status` exits 0 on
  them; the next `push` / `pull` writes them to the state.
- The backup holds the card directory under `CARD/` and the host files a
  `pull` or `resolve` overwrites under `HOST/`. Pruning keeps the last 10 of
  cardsync's own (`YYYYMMDD-HHMMSS[-N]`) in the project's own
  `.cardsync/backup`; any other directory there is left alone.
- `resolve FILE card|local`: FILE in either form (`SRC\MAIN.Z8A`,
  `src/main.z8a`); when the chosen side has no file, the other side's is
  deleted (backed up first).
- First real use (2026-11-24, WRECK): `status` found `SRC/MAIN.Z8A` changed
  on the MSX only (`DI` / `LD SP,#F380`, not in the repo) as a conflict, every
  other file equal; `resolve SRC/MAIN.Z8A card` brought it to the host, `push`
  recorded the state, `status` "nothing to do".
- Tests: `scripts/test_cardsync.py`, 33 cases (a row of 4 a case, both
  directions; names, ignore, backups and pruning, read-back injected, dry
  run, status, init, resolve, usage) and 20 mutations, all killed
  (`python3 scripts/test_cardsync.py --mutations`).
