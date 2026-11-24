#!/usr/bin/env python3
"""test_cardsync.py -- cardsync (CARDSYNC.md 8) on a fake card.

    python3 test_cardsync.py              the cases (unittest)
    python3 test_cardsync.py --mutations  every mutation must fail them

The card is a temporary directory (CARDSYNC_ROOT, no FAT check). One case
per row of the rules' table (CARDSYNC.md 4) in both directions, then names,
ignore, backup, read-back, dry run, status, init and resolve. CARDSYNC_PY
names the cardsync.py under test (a mutant, for --mutations).
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.environ.get('CARDSYNC_PY', os.path.join(HERE, 'cardsync.py'))


def load():
    spec = importlib.util.spec_from_file_location('cardsync_under_test', TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cs = load()

CFG = """[card]
volume  = WORK            ; the card's volume
dir     = DEV\\PROJ
[local]
dir     = MSX
subdirs = SRC GFX
ignore  = *.REL *.SYM
"""


class Base(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.prj = os.path.join(self.tmp, 'prj')
        self.host = os.path.join(self.prj, 'MSX')
        self.vols = os.path.join(self.tmp, 'vols')
        self.card = os.path.join(self.vols, 'WORK', 'DEV', 'PROJ')
        os.makedirs(self.host)
        os.makedirs(self.card)
        with open(os.path.join(self.prj, 'cardsync.cfg'), 'w') as fh:
            fh.write(CFG)
        self.env = dict(os.environ)
        os.environ['CARDSYNC_ROOT'] = self.vols
        self.cwd = os.getcwd()
        os.chdir(self.prj)

    def tearDown(self):
        os.chdir(self.cwd)
        os.environ.clear()
        os.environ.update(self.env)
        shutil.rmtree(self.tmp)

    # helpers

    def put(self, side, rel, data):
        top = self.host if side == 'host' else self.card
        p = os.path.join(top, *rel.split('/'))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as fh:
            fh.write(data)

    def get(self, side, rel):
        top = self.host if side == 'host' else self.card
        p = os.path.join(top, *rel.split('/'))
        if not os.path.exists(p):
            return None
        with open(p, 'rb') as fh:
            return fh.read()

    def rm(self, side, rel):
        top = self.host if side == 'host' else self.card
        os.remove(os.path.join(top, *rel.split('/')))

    def run_cs(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cs.main(list(argv))
        self.out = out.getvalue()
        return code

    def state(self):
        p = os.path.join(self.prj, '.cardsync', 'state.json')
        if not os.path.exists(p):
            return None
        with open(p) as fh:
            return json.load(fh)

    def synced(self, files):
        """Both sides hold files (rel: bytes), recorded by a push."""
        for rel, data in files.items():
            self.put('host', rel, data)
        self.assertEqual(self.run_cs('push'), 0, self.out)
        for rel, data in files.items():
            self.assertEqual(self.get('card', rel), data)

    def backups(self):
        d = os.path.join(self.prj, '.cardsync', 'backup')
        return sorted(os.listdir(d)) if os.path.isdir(d) else []


class Rules(Base):
    """CARDSYNC.md 4, a case a row."""

    def test_same_same_nothing(self):
        self.synced({'A.TXT': b'1'})
        n = len(self.backups())
        self.assertEqual(self.run_cs('push'), 0)
        self.assertEqual(self.run_cs('pull'), 0)
        self.assertEqual(len(self.backups()), n)        # nothing written
        self.assertEqual(self.run_cs('status'), 0)

    def test_card_changed_pull_copies(self):
        self.synced({'SRC/M.Z8A': b'old\r\n'})
        self.put('card', 'SRC/M.Z8A', b'new\r\n')
        self.assertEqual(self.run_cs('pull'), 0, self.out)
        self.assertEqual(self.get('host', 'SRC/M.Z8A'), b'new\r\n')
        self.assertEqual(self.run_cs('status'), 0, self.out)

    def test_card_changed_push_leaves_it(self):
        self.synced({'SRC/M.Z8A': b'old'})
        self.put('card', 'SRC/M.Z8A', b'new')
        self.assertEqual(self.run_cs('push'), 0)
        self.assertIn('newer on card', self.out)
        self.assertEqual(self.get('card', 'SRC/M.Z8A'), b'new')
        self.assertEqual(self.get('host', 'SRC/M.Z8A'), b'old')

    def test_host_changed_push_copies(self):
        self.synced({'MAKEFILE': b'a'})
        self.put('host', 'MAKEFILE', b'b')
        self.assertEqual(self.run_cs('push'), 0)
        self.assertEqual(self.get('card', 'MAKEFILE'), b'b')

    def test_host_changed_pull_leaves_it(self):
        self.synced({'MAKEFILE': b'a'})
        self.put('host', 'MAKEFILE', b'b')
        self.assertEqual(self.run_cs('pull'), 0)
        self.assertIn('newer on host', self.out)
        self.assertEqual(self.get('host', 'MAKEFILE'), b'b')
        self.assertEqual(self.get('card', 'MAKEFILE'), b'a')

    def test_both_changed_differ_conflict(self):
        self.synced({'A.TXT': b'0', 'B.TXT': b'0'})
        self.put('host', 'A.TXT', b'h')
        self.put('card', 'A.TXT', b'c')
        self.put('host', 'B.TXT', b'h2')            # pending, not written
        for cmd in ('push', 'pull'):
            self.assertEqual(self.run_cs(cmd), 1, self.out)
            self.assertIn('CONFLICT', self.out)
        self.assertEqual(self.get('card', 'B.TXT'), b'0')
        self.assertEqual(self.get('card', 'A.TXT'), b'c')
        self.assertEqual(self.get('host', 'A.TXT'), b'h')

    def test_both_changed_equal_record(self):
        self.synced({'A.TXT': b'0'})
        self.put('host', 'A.TXT', b'same')
        self.put('card', 'A.TXT', b'same')
        self.assertEqual(self.run_cs('status'), 0, self.out)
        self.assertEqual(self.run_cs('pull'), 0)
        self.assertEqual(self.state()['A.TXT'], cs.sha(os.path.join(self.host, 'A.TXT')))

    def test_new_host_push_copies_pull_not(self):
        self.put('host', 'GFX/T.SR2', b'x')
        self.assertEqual(self.run_cs('pull'), 0)
        self.assertIsNone(self.get('card', 'GFX/T.SR2'))
        self.assertIn('new on host', self.out)
        self.assertEqual(self.run_cs('push'), 0)
        self.assertEqual(self.get('card', 'GFX/T.SR2'), b'x')

    def test_new_card_pull_copies_push_not(self):
        self.put('card', 'SRC/N.Z8A', b'y')
        self.assertEqual(self.run_cs('push'), 0)
        self.assertIsNone(self.get('host', 'SRC/N.Z8A'))
        self.assertEqual(self.run_cs('pull'), 0)
        self.assertEqual(self.get('host', 'SRC/N.Z8A'), b'y')

    def test_unrecorded_equal_record(self):
        self.put('host', 'A.TXT', b'e')
        self.put('card', 'A.TXT', b'e')
        self.assertEqual(self.run_cs('push'), 0)
        self.assertIn('A.TXT', self.state())

    def test_unrecorded_differ_conflict(self):
        self.put('host', 'SRC/MAIN.Z8A', b'repo')
        self.put('card', 'SRC/MAIN.Z8A', b'msx')
        self.assertEqual(self.run_cs('status'), 1)
        self.assertIn('CONFLICT', self.out)
        self.assertEqual(self.run_cs('push'), 1)
        self.assertEqual(self.get('card', 'SRC/MAIN.Z8A'), b'msx')
        self.assertIsNone(self.state())

    def test_host_deleted_push_keeps_without_delete(self):
        self.synced({'A.TXT': b'1'})
        self.rm('host', 'A.TXT')
        self.assertEqual(self.run_cs('push'), 0)
        self.assertEqual(self.get('card', 'A.TXT'), b'1')
        self.assertEqual(self.run_cs('push', '--delete'), 0)
        self.assertIsNone(self.get('card', 'A.TXT'))
        self.assertNotIn('A.TXT', self.state())

    def test_card_deleted_pull_delete(self):
        self.synced({'A.TXT': b'1'})
        self.rm('card', 'A.TXT')
        self.assertEqual(self.run_cs('pull'), 0)
        self.assertEqual(self.get('host', 'A.TXT'), b'1')
        self.assertEqual(self.run_cs('push', '--delete'), 0)   # the card's: not push's
        self.assertEqual(self.get('host', 'A.TXT'), b'1')
        self.assertEqual(self.run_cs('pull', '--delete'), 0)
        self.assertIsNone(self.get('host', 'A.TXT'))

    def test_deleted_one_changed_other_conflict(self):
        self.synced({'A.TXT': b'1'})
        self.rm('host', 'A.TXT')
        self.put('card', 'A.TXT', b'2')
        self.assertEqual(self.run_cs('push', '--delete'), 1)
        self.assertEqual(self.get('card', 'A.TXT'), b'2')


class Names(Base):

    def test_refused_names_warned_not_copied(self):
        self.put('host', 'lower.txt', b'1')
        self.put('host', 'TOOLONGNAME.TXT', b'1')
        self.put('host', 'OK.TXT', b'1')
        self.assertEqual(self.run_cs('push'), 0)
        self.assertIn('lower.txt refused', self.out)
        self.assertIn('TOOLONGNAME.TXT refused', self.out)
        self.assertEqual(sorted(os.listdir(self.card)), ['OK.TXT'])

    def test_silent_and_ignored(self):
        self.put('host', '._OK.TXT', b'x')
        self.put('host', '.DS_Store', b'x')
        self.put('host', 'SRC/M.REL', b'x')
        self.put('card', 'GFX/T.SYM', b'x')
        self.assertEqual(self.run_cs('status'), 0, self.out)
        self.assertNotIn('DS_Store', self.out)
        self.assertEqual(self.run_cs('push'), 0)
        self.assertIsNone(self.get('card', 'SRC/M.REL'))

    def test_unlisted_subdir_reported(self):
        self.put('card', 'OBJ/X.REL', b'x')
        self.put('card', 'OBJ/X.BIN', b'x')
        self.assertEqual(self.run_cs('pull'), 0)
        self.assertIn('OBJ/ not synced', self.out)
        self.assertFalse(os.path.exists(os.path.join(self.host, 'OBJ')))

    def test_bytes_kept(self):
        data = b'LD A,1\r\n\x1a'
        self.put('host', 'SRC/A.Z8A', data)
        self.assertEqual(self.run_cs('push'), 0)
        self.assertEqual(self.get('card', 'SRC/A.Z8A'), data)


class Writing(Base):

    def test_backup_of_card_before_write(self):
        self.synced({'A.TXT': b'old'})
        self.put('host', 'A.TXT', b'new')
        before = self.backups()
        self.assertEqual(self.run_cs('push'), 0)
        new = [b for b in self.backups() if b not in before]
        self.assertEqual(len(new), 1)
        with open(os.path.join(self.prj, '.cardsync', 'backup', new[0], 'CARD', 'A.TXT'),
                  'rb') as fh:
            self.assertEqual(fh.read(), b'old')

    def test_backup_of_host_before_pull(self):
        self.synced({'A.TXT': b'old'})
        self.put('card', 'A.TXT', b'new')
        before = self.backups()
        self.assertEqual(self.run_cs('pull'), 0)
        new = [b for b in self.backups() if b not in before]
        with open(os.path.join(self.prj, '.cardsync', 'backup', new[0], 'HOST', 'A.TXT'),
                  'rb') as fh:
            self.assertEqual(fh.read(), b'old')

    def test_backups_pruned_to_ten_own_only(self):
        d = os.path.join(self.prj, '.cardsync', 'backup')
        os.makedirs(os.path.join(d, 'manual-keep'))
        for i in range(12):
            os.makedirs(os.path.join(d, '20200101-0000%02d' % i))
        self.put('host', 'A.TXT', b'1')
        self.assertEqual(self.run_cs('push'), 0)
        own = [b for b in self.backups() if b != 'manual-keep']
        self.assertEqual(len(own), 10)
        self.assertIn('manual-keep', self.backups())

    def test_readback_mismatch(self):
        self.synced({'A.TXT': b'1'})
        self.put('host', 'A.TXT', b'2')
        st = self.state()
        real = cs.copy_file

        def bad(src, dst):
            real(src, dst)
            with open(dst, 'ab') as fh:
                fh.write(b'!')
        cs.copy_file = bad
        try:
            self.assertEqual(self.run_cs('push'), 4, self.out)
        finally:
            cs.copy_file = real
        self.assertEqual(self.state(), st)

    def test_dry_run_writes_nothing(self):
        self.put('host', 'A.TXT', b'1')
        self.put('card', 'B.TXT', b'2')
        for argv in (('-n', 'push'), ('-n', 'pull'), ('-n', 'init')):
            self.assertEqual(self.run_cs(*argv), 0, self.out)
        self.assertIsNone(self.get('card', 'A.TXT'))
        self.assertIsNone(self.get('host', 'B.TXT'))
        self.assertIsNone(self.state())
        self.assertEqual(self.backups(), [])

    def test_appledouble_removed(self):
        self.put('host', 'A.TXT', b'1')
        self.put('card', '._B.TXT', b'junk')
        self.assertEqual(self.run_cs('push'), 0)
        self.assertIsNone(self.get('card', '._B.TXT'))

    def test_card_not_mounted(self):
        shutil.rmtree(os.path.join(self.vols, 'WORK'))
        self.assertEqual(self.run_cs('push'), 3)
        self.assertEqual(self.run_cs('status'), 3)


class Commands(Base):

    def test_status_pending_exit_1(self):
        self.put('host', 'A.TXT', b'1')
        self.assertEqual(self.run_cs('status'), 1)
        self.assertIn('new on host', self.out)

    def test_init_empty_card(self):
        shutil.rmtree(self.card)
        self.put('host', 'MAKEFILE', b'm')
        self.put('host', 'SRC/A.Z8A', b'a')
        self.assertEqual(self.run_cs('init'), 0, self.out)
        self.assertEqual(self.get('card', 'SRC/A.Z8A'), b'a')
        self.assertTrue(os.path.isdir(os.path.join(self.card, 'GFX')))
        self.assertEqual(sorted(self.state()), ['MAKEFILE', 'SRC/A.Z8A'])

    def test_init_empty_host(self):
        self.put('card', 'A.TXT', b'c')
        self.assertEqual(self.run_cs('init'), 0)
        self.assertEqual(self.get('host', 'A.TXT'), b'c')

    def test_init_both_refused_when_differ(self):
        self.put('host', 'A.TXT', b'1')
        self.put('card', 'A.TXT', b'2')
        self.assertEqual(self.run_cs('init'), 1)
        self.assertIsNone(self.state())
        self.put('card', 'A.TXT', b'1')
        self.assertEqual(self.run_cs('init'), 0)
        self.assertEqual(list(self.state()), ['A.TXT'])

    def test_resolve_card(self):
        self.put('host', 'SRC/MAIN.Z8A', b'repo')
        self.put('card', 'SRC/MAIN.Z8A', b'msx')
        self.assertEqual(self.run_cs('resolve', 'SRC\\MAIN.Z8A', 'card'), 0, self.out)
        self.assertEqual(self.get('host', 'SRC/MAIN.Z8A'), b'msx')
        self.assertEqual(self.run_cs('status'), 0, self.out)

    def test_resolve_local(self):
        self.put('host', 'A.TXT', b'repo')
        self.put('card', 'A.TXT', b'msx')
        self.assertEqual(self.run_cs('resolve', 'a.txt', 'local'), 0)
        self.assertEqual(self.get('card', 'A.TXT'), b'repo')

    def test_resolve_deleted_side(self):
        self.synced({'A.TXT': b'1'})
        self.rm('host', 'A.TXT')
        self.put('card', 'A.TXT', b'2')
        self.assertEqual(self.run_cs('resolve', 'A.TXT', 'local'), 0)
        self.assertIsNone(self.get('card', 'A.TXT'))
        self.assertNotIn('A.TXT', self.state())

    def test_usage(self):
        self.assertEqual(self.run_cs('resolve', 'A.TXT'), 2)
        self.assertEqual(self.run_cs('push', 'A.TXT'), 2)
        os.remove(os.path.join(self.prj, 'cardsync.cfg'))
        self.assertEqual(self.run_cs('status'), 2)


# --- mutations: each breaks one rule; the cases must fail --------------------

MUTATIONS = [
    ('record-as-conflict', "return 'record' if l == c else 'conflict'", "return 'conflict'"),
    ('conflict-as-record', "return 'record' if l == c else 'conflict'", "return 'record'"),
    ('changed-equal-conflict', "if ls == 'changed' and cs == 'changed' and l == c:",
     "if False:"),
    ('newer-card-swapped', "return 'newer-card' if cs == 'changed' else 'gone-card'",
     "return 'newer-host' if cs == 'changed' else 'gone-card'"),
    ('conflicts-written', "    conflicts_stop(rows)\n    w = Writer", "    w = Writer"),
    ('both-directions', "elif k in ('newer-' + mine, 'new-' + mine):",
     "elif k.startswith(('newer-', 'new-')):"),
    ('delete-always', "            if args.delete:\n                w.delete",
     "            if True:\n                w.delete"),
    ('no-card-backup', "            backup_card(self.prj, self._backup_dir())",
     "            self._backup_dir()"),
    ('no-host-backup', "        if os.path.exists(old):\n            copy_file",
     "        if False:\n            copy_file"),
    ('no-readback', "        if bad:\n            raise Fail(EXIT_READBACK",
     "        if False:\n            raise Fail(EXIT_READBACK"),
    ('dry-writes', "        if self.dry:\n            return\n        if to_card:",
     "        if to_card:"),
    ('names-unchecked', "            if not NAME_RE.match(name):", "            if False:"),
    ('ignore-off', "            if any(fnmatch.fnmatchcase(name.upper(), pat) for pat in prj.ignore):",
     "            if False:"),
    ('subdirs-any', "                if not rel and name in prj.subdirs:", "                if not rel:"),
    ('prune-all', "    for d in mine[:-BACKUPS_KEPT]:", "    for d in mine:"),
    ('appledouble-kept', "        if self.card_touched:\n            clean_appledouble",
     "        if False:\n            clean_appledouble"),
    ('init-unequal', "        if differ:\n            for p in differ:",
     "        if False:\n            for p in differ:"),
    ('resolve-reversed', "    to_card = args.side == 'local'", "    to_card = args.side == 'card'"),
    ('status-always-ok', "    return EXIT_PENDING if pending else EXIT_OK", "    return EXIT_OK"),
    ('mount-unchecked', "        if not os.path.isdir(self.vol_path):", "        if False:"),
]


def run_mutations():
    src = open(TOOL).read()
    survived = []
    with tempfile.TemporaryDirectory() as t:
        for name, old, new in MUTATIONS:
            if src.count(old) != 1:
                print('  STALE  %-24s anchor found %d times' % (name, src.count(old)))
                survived.append(name)
                continue
            mut = os.path.join(t, 'cardsync.py')
            with open(mut, 'w') as fh:
                fh.write(src.replace(old, new))
            env = dict(os.environ, CARDSYNC_PY=mut)
            r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env,
                               capture_output=True, text=True)
            ok = r.returncode != 0
            print('  %s  %-24s %s' % ('ok  ' if ok else 'FAIL', name,
                                     'killed' if ok else 'SURVIVED'))
            if not ok:
                survived.append(name)
    print('%d mutations, %d not killed' % (len(MUTATIONS), len(survived)))
    return 1 if survived else 0


if __name__ == '__main__':
    if '--mutations' in sys.argv:
        sys.exit(run_mutations())
    unittest.main()
