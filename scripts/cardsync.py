#!/usr/bin/env python3
"""cardsync -- keep a project's MSX tree in step with the Nextor SD card.

Specification: msxtools/CARDSYNC.md (rev 3). The repository is the truth,
the card a working copy. Changes are found by content hash against the last
sync (.cardsync/state.json beside cardsync.cfg), never by dates nor by the
FAT archive bit (that one belongs to SMAKE). A file changed on both sides is
a conflict: the whole run writes nothing. cardsync never runs git.

    cardsync [-n] [--eject] init
    cardsync status
    cardsync [-n] [--delete] [--eject] pull
    cardsync [-n] [--delete] [--eject] push
    cardsync [-n] resolve FILE card|local

Exit codes: 0 done / nothing to do, 1 conflicts (or, for status, pending
changes), 2 usage or cfg error, 3 card not mounted / not FAT, 4 read-back
mismatch. CARDSYNC_ROOT replaces /Volumes and skips the FAT check (tests).
"""

import argparse
import configparser
import fnmatch
import hashlib
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import time

CFG_NAME = 'cardsync.cfg'
STATE_DIR = '.cardsync'
BACKUPS_KEPT = 10
NAME_RE = re.compile(r'^[A-Z0-9_$#%&!-]{1,8}(\.[A-Z0-9_$#%&!-]{1,3})?$')
SILENT = ('.DS_Store', '.Trashes', '.Spotlight-V100', '.fseventsd',
          'System Volume Information')
STAMP_RE = re.compile(r'^\d{8}-\d{6}(-\d+)?$')

EXIT_OK, EXIT_PENDING, EXIT_USAGE, EXIT_CARD, EXIT_READBACK = 0, 1, 2, 3, 4


class Fail(Exception):
    """A run that stops: its message and exit code."""

    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code


# --- configuration -------------------------------------------------------


def find_cfg(start):
    d = os.path.abspath(start)
    while True:
        p = os.path.join(d, CFG_NAME)
        if os.path.isfile(p):
            return p
        up = os.path.dirname(d)
        if up == d:
            raise Fail(EXIT_USAGE, 'no %s here or in a parent directory' % CFG_NAME)
        d = up


class Project:
    """cardsync.cfg read: where the card's directory and the host's are."""

    def __init__(self, cfg_path):
        cp = configparser.ConfigParser(inline_comment_prefixes=(';',))
        try:
            cp.read(cfg_path)
            volume = cp.get('card', 'volume').strip()
            cdir = cp.get('card', 'dir').strip()
            ldir = cp.get('local', 'dir').strip()
            subdirs = cp.get('local', 'subdirs', fallback='').split()
            ignore = cp.get('local', 'ignore', fallback='').split()
        except (configparser.Error, OSError) as e:
            raise Fail(EXIT_USAGE, '%s: %s' % (cfg_path, e))
        parts = [p for p in re.split(r'[\\/]', cdir) if p]
        for p in parts + subdirs:
            if not NAME_RE.match(p):
                raise Fail(EXIT_USAGE, '%s: %r is not an 8.3 name' % (cfg_path, p))
        self.root = os.path.dirname(os.path.abspath(cfg_path))
        self.volume = volume
        self.card_root = os.environ.get('CARDSYNC_ROOT', '/Volumes')
        self.testing = 'CARDSYNC_ROOT' in os.environ
        self.vol_path = os.path.join(self.card_root, volume)
        self.card = os.path.join(self.vol_path, *parts)
        self.card_name = '\\'.join(parts)
        self.local = os.path.join(self.root, ldir)
        self.subdirs = subdirs
        self.ignore = [i.upper() for i in ignore]
        self.state_path = os.path.join(self.root, STATE_DIR, 'state.json')
        self.backups = os.path.join(self.root, STATE_DIR, 'backup')

    def check_card(self):
        """The card mounted and FAT (not under CARDSYNC_ROOT)."""
        if not os.path.isdir(self.vol_path):
            raise Fail(EXIT_CARD, 'card not mounted: %s' % self.vol_path)
        if self.testing:
            return
        try:
            out = subprocess.run(['diskutil', 'info', '-plist', self.vol_path],
                                 capture_output=True, check=True).stdout
            info = plistlib.loads(out)
        except (OSError, subprocess.CalledProcessError, plistlib.InvalidFileException):
            raise Fail(EXIT_CARD, 'diskutil cannot read %s' % self.vol_path)
        fs = (info.get('FilesystemType', '') + ' ' + info.get('FilesystemName', '')).lower()
        if 'msdos' not in fs and 'fat' not in fs:
            raise Fail(EXIT_CARD, '%s is not a FAT volume (%s)' % (self.vol_path, fs.strip()))

    def load_state(self):
        try:
            with open(self.state_path) as fh:
                return json.load(fh)
        except FileNotFoundError:
            return {}
        except (OSError, ValueError) as e:
            raise Fail(EXIT_USAGE, '%s: %s' % (self.state_path, e))

    def save_state(self, state):
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        tmp = self.state_path + '.tmp'
        with open(tmp, 'w') as fh:
            json.dump(dict(sorted(state.items())), fh, indent=1)
            fh.write('\n')
        os.replace(tmp, self.state_path)


# --- scanning ------------------------------------------------------------


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def silent(name):
    return name.startswith('._') or name in SILENT


def scan(prj, top, side, notes):
    """{relative path: hash} of one side; refused names and unlisted
    sub-directories go to notes. relative paths: NAME.EXT or SUB/NAME.EXT"""
    files = {}
    if not os.path.isdir(top):
        return files

    def files_in(d, rel):
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            r = rel + name
            if silent(name):
                continue
            if os.path.isdir(p):
                if not rel and name in prj.subdirs:
                    files_in(p, name + '/')
                else:
                    notes.append('%s: %s/ not synced (not a listed sub-directory)' % (side, r))
                continue
            if not NAME_RE.match(name):
                notes.append('%s: %s refused (not an upper-case 8.3 name)' % (side, r))
                continue
            if any(fnmatch.fnmatchcase(name.upper(), pat) for pat in prj.ignore):
                continue
            files[r] = sha(p)

    files_in(top, '')
    return files


def path_of(top, rel):
    return os.path.join(top, *rel.split('/'))


# --- the rules (CARDSYNC.md 4) -------------------------------------------


def classify(l, c, s):
    """One path: l, c, s = host, card, state hashes (None: absent)."""
    if s is None:
        if l is not None and c is not None:
            return 'record' if l == c else 'conflict'
        return 'new-host' if l is not None else 'new-card'
    ls = 'same' if l == s else ('gone' if l is None else 'changed')
    cs = 'same' if c == s else ('gone' if c is None else 'changed')
    if ls == 'same' and cs == 'same':
        return 'nothing'
    if ls == 'same':
        return 'newer-card' if cs == 'changed' else 'gone-card'
    if cs == 'same':
        return 'newer-host' if ls == 'changed' else 'gone-host'
    if ls == 'gone' and cs == 'gone':
        return 'forget'
    if ls == 'changed' and cs == 'changed' and l == c:
        return 'record'
    return 'conflict'


LABELS = {
    'newer-card': 'newer on card', 'newer-host': 'newer on host',
    'new-card': 'new on card', 'new-host': 'new on host',
    'gone-card': 'deleted on card', 'gone-host': 'deleted on host',
    'conflict': 'CONFLICT', 'record': 'equal, not recorded yet',
    'forget': 'deleted on both sides',
}


def plan(prj):
    notes = []
    host = scan(prj, prj.local, 'host', notes)
    card = scan(prj, prj.card, 'card', notes)
    state = prj.load_state()
    paths = sorted(set(host) | set(card) | set(state))
    rows = [(p, classify(host.get(p), card.get(p), state.get(p))) for p in paths]
    return host, card, state, rows, notes


# --- writing -------------------------------------------------------------


def copy_file(src, dst):
    """Bytes only, no extended attributes, the mtime kept."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    st = os.stat(src)
    os.utime(dst, (st.st_atime, st.st_mtime))


def new_backup(prj):
    os.makedirs(prj.backups, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    d = os.path.join(prj.backups, stamp)
    n = 1
    while os.path.exists(d):
        n += 1
        d = os.path.join(prj.backups, '%s-%d' % (stamp, n))
    os.makedirs(d)
    return d


def prune_backups(prj):
    """The last BACKUPS_KEPT of cardsync's own (YYYYMMDD-HHMMSS[-N])."""
    if not os.path.isdir(prj.backups):
        return
    mine = sorted(d for d in os.listdir(prj.backups)
                  if STAMP_RE.match(d) and os.path.isdir(os.path.join(prj.backups, d)))
    for d in mine[:-BACKUPS_KEPT]:
        shutil.rmtree(os.path.join(prj.backups, d))


def backup_card(prj, dst):
    """The whole card directory, before its first write."""
    if not os.path.isdir(prj.card):
        return
    for top, dirs, files in os.walk(prj.card):
        dirs[:] = [d for d in dirs if not silent(d)]
        rel = os.path.relpath(top, prj.card)
        for f in files:
            if silent(f):
                continue
            copy_file(os.path.join(top, f), os.path.join(dst, 'CARD', rel, f))


def clean_appledouble(top):
    for d, dirs, files in os.walk(top):
        dirs[:] = [x for x in dirs if not silent(x)]
        for f in files:
            if f.startswith('._'):
                os.remove(os.path.join(d, f))


class Writer:
    """Copies and deletions of one run, read back, then the state."""

    def __init__(self, prj, dry):
        self.prj, self.dry = prj, dry
        self.backup = None
        self.card_saved = False
        self.written = []          # (path, hash wanted)
        self.card_touched = False

    def _backup_dir(self):
        if self.backup is None:
            self.backup = new_backup(self.prj)
        return self.backup

    def _before_card_write(self):
        if not self.card_saved:
            backup_card(self.prj, self._backup_dir())
            self.card_saved = True
        self.card_touched = True

    def _before_host_write(self, rel):
        old = path_of(self.prj.local, rel)
        if os.path.exists(old):
            copy_file(old, path_of(os.path.join(self._backup_dir(), 'HOST'), rel))

    def copy(self, rel, to_card, want):
        src = path_of(self.prj.local if to_card else self.prj.card, rel)
        dst = path_of(self.prj.card if to_card else self.prj.local, rel)
        print('  %s %s' % ('->' if to_card else '<-', rel))
        if self.dry:
            return
        if to_card:
            self._before_card_write()
        else:
            self._before_host_write(rel)
        copy_file(src, dst)
        self.written.append((dst, want))

    def delete(self, rel, on_card):
        p = path_of(self.prj.card if on_card else self.prj.local, rel)
        print('  rm %s %s' % ('card' if on_card else 'host', rel))
        if self.dry:
            return
        if on_card:
            self._before_card_write()
        else:
            self._before_host_write(rel)
        os.remove(p)

    def finish(self, state):
        """AppleDouble out, sync, every written file read back, then the
        state (last); a mismatch leaves the state as it was."""
        if self.dry:
            return
        if self.card_touched:
            clean_appledouble(self.prj.card)
        os.sync()
        bad = [p for p, want in self.written if sha(p) != want]
        if bad:
            raise Fail(EXIT_READBACK, 'read-back mismatch: %s (state not changed)' % ', '.join(bad))
        self.prj.save_state(state)
        if self.backup:
            prune_backups(self.prj)


# --- commands ------------------------------------------------------------


def show_notes(notes):
    for n in notes:
        print('warning: ' + n)


def cmd_status(prj, args):
    prj.check_card()
    _, _, _, rows, notes = plan(prj)
    show_notes(notes)
    pending = False
    for p, k in rows:
        if k == 'nothing':
            continue
        print('  %-24s %s' % (p, LABELS[k]))
        pending |= k != 'record'
    if not pending:
        print('nothing to do')
    return EXIT_PENDING if pending else EXIT_OK


def conflicts_stop(rows):
    bad = [p for p, k in rows if k == 'conflict']
    if bad:
        for p in bad:
            print('  %-24s CONFLICT' % p)
        raise Fail(EXIT_PENDING, '%d conflict(s): nothing written; cardsync resolve FILE '
                                 'card|local' % len(bad))


def cmd_sync(prj, args, to_card):
    prj.check_card()
    host, card, state, rows, notes = plan(prj)
    show_notes(notes)
    conflicts_stop(rows)
    w = Writer(prj, args.n)
    new = dict(state)
    mine, theirs = ('host', 'card') if to_card else ('card', 'host')
    for p, k in rows:
        if k == 'nothing':
            continue
        if k == 'record':
            new[p] = host[p]
        elif k == 'forget':
            new.pop(p, None)
        elif k in ('newer-' + mine, 'new-' + mine):
            want = host[p] if to_card else card[p]
            w.copy(p, to_card, want)
            new[p] = want
        elif k == 'gone-' + mine:
            if args.delete:
                w.delete(p, on_card=to_card)
                new.pop(p, None)
            else:
                print('  %-24s deleted on %s: kept (--delete removes it)' % (p, mine))
        else:                       # the other side's: never touched
            print('  %-24s %s: not touched by %s' % (p, LABELS[k],
                                                     'push' if to_card else 'pull'))
    w.finish(new)
    if args.n:
        print('dry run: nothing written')
    return EXIT_OK


def cmd_init(prj, args):
    prj.check_card()
    host, card, state, rows, notes = plan(prj)
    show_notes(notes)
    w = Writer(prj, args.n)
    if not card:
        print('init: %s gets the host\'s files' % prj.card_name)
        if not args.n:
            for sub in [''] + prj.subdirs:
                os.makedirs(os.path.join(prj.card, sub), exist_ok=True)
        new = {}
        for p in sorted(host):
            w.copy(p, True, host[p])
            new[p] = host[p]
    elif not host:
        print('init: the host gets %s\'s files' % prj.card_name)
        new = {}
        for p in sorted(card):
            w.copy(p, False, card[p])
            new[p] = card[p]
    else:
        differ = [p for p in sorted(set(host) & set(card)) if host[p] != card[p]]
        if differ:
            for p in differ:
                print('  %-24s differs' % p)
            raise Fail(EXIT_PENDING, 'init: both sides hold files and %d differ: nothing '
                                     'written' % len(differ))
        new = {p: host[p] for p in set(host) & set(card)}
        print('init: both sides equal where they meet: %d recorded' % len(new))
    w.finish(new)
    if args.n:
        print('dry run: nothing written')
    return EXIT_OK


def cmd_resolve(prj, args):
    prj.check_card()
    rel = args.file.replace('\\', '/').upper()
    host, card, state, rows, notes = plan(prj)
    if rel not in dict(rows):
        raise Fail(EXIT_USAGE, '%s: not a synced path' % rel)
    w = Writer(prj, args.n)
    new = dict(state)
    to_card = args.side == 'local'
    src = host if to_card else card
    if rel in src:
        w.copy(rel, to_card, src[rel])
        new[rel] = src[rel]
    else:
        other = card if to_card else host
        if rel in other:
            w.delete(rel, on_card=to_card)
        new.pop(rel, None)
    w.finish(new)
    if args.n:
        print('dry run: nothing written')
    return EXIT_OK


def eject(prj):
    if prj.testing:
        return
    out = subprocess.run(['diskutil', 'info', '-plist', prj.vol_path],
                         capture_output=True).stdout
    try:
        whole = plistlib.loads(out).get('ParentWholeDisk')
    except plistlib.InvalidFileException:
        whole = None
    if not whole:
        raise Fail(EXIT_CARD, 'cannot find the disk of %s to eject' % prj.vol_path)
    subprocess.run(['diskutil', 'eject', whole], check=False)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='cardsync', description=__doc__.split('\n')[0])
    ap.add_argument('-n', action='store_true', help='dry run: write nothing')
    ap.add_argument('--delete', action='store_true', help='propagate deletions')
    ap.add_argument('--eject', action='store_true', help='eject the card after a run')
    ap.add_argument('command', choices=('init', 'status', 'pull', 'push', 'resolve'))
    ap.add_argument('file', nargs='?')
    ap.add_argument('side', nargs='?', choices=('card', 'local'))
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return EXIT_USAGE if e.code else EXIT_OK
    try:
        if args.command == 'resolve':
            if not args.file or not args.side:
                raise Fail(EXIT_USAGE, 'resolve FILE card|local')
        elif args.file:
            raise Fail(EXIT_USAGE, '%s takes no FILE' % args.command)
        prj = Project(find_cfg(os.getcwd()))
        if args.command == 'status':
            code = cmd_status(prj, args)
        elif args.command == 'init':
            code = cmd_init(prj, args)
        elif args.command == 'resolve':
            code = cmd_resolve(prj, args)
        else:
            code = cmd_sync(prj, args, args.command == 'push')
        if args.eject and code == EXIT_OK and not args.n:
            eject(prj)
        return code
    except Fail as e:
        print('cardsync: %s' % e, file=sys.stderr)
        return e.code


if __name__ == '__main__':
    sys.exit(main())
