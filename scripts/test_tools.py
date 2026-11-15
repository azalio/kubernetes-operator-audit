#!/usr/bin/env python3
"""Synthetic tool tests; do not claim Kubernetes integration coverage."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

v = load('validate_report')
inv = load('inventory')

class ReportTests(unittest.TestCase):
    def base(self):
        return {'scope': {'repository': 'synthetic-fixture', 'revision': 'fixture-v1', 'mode': 'full', 'limitations': ['Static test only']},
                'checks': [{'id': 'M-01', 'status': 'unknown', 'reason': 'No implementation supplied', 'evidence': []}],
                'findings': [], 'tests': []}

    def test_unknown_is_honest(self):
        self.assertEqual(v.validate(self.base(), ['M-01']), [])

    def test_missing_coverage(self):
        self.assertTrue(v.validate(self.base(), ['M-01', 'M-02']))

    def test_pass_without_evidence(self):
        d = self.base(); d['checks'][0]['status'] = 'pass'
        self.assertTrue(v.validate(d, ['M-01']))

    def test_evidenced_static_pass(self):
        d = self.base(); d['checks'][0].update(status='pass', evidence=['fixture.go:1-9: deterministic pure transformation'])
        self.assertEqual(v.validate(d, ['M-01']), [])

    def test_fail_without_finding(self):
        d = self.base(); d['checks'][0].update(status='fail', evidence=['fixture.go:1'])
        self.assertTrue(v.validate(d, ['M-01']))

    def test_na_requires_reason(self):
        d = self.base(); d['checks'][0].update(status='not_applicable', reason='')
        self.assertTrue(v.validate(d, ['M-01']))

    def test_duplicate_check(self):
        d = self.base(); d['checks'].append(copy.deepcopy(d['checks'][0]))
        self.assertTrue(v.validate(d, ['M-01']))

    def test_false_test_result(self):
        d = self.base(); d['tests'] = [{'command':'test', 'environment':'fixture', 'status':'passed', 'exit_code':1, 'artifact':'log'}]
        self.assertTrue(v.validate(d, ['M-01']))

    def test_bad_document_types(self):
        for d in (None, [], {'checks': [None], 'tests': [None], 'findings': [None]}):
            self.assertTrue(v.validate(d, ['M-01']))

    def test_complete_catalog(self):
        ids = v.catalog()
        self.assertEqual(len(ids), len(set(ids)))
        for n in range(1, 12):
            self.assertTrue(any(x.startswith('B%02d-' % n) for x in ids))
        self.assertEqual(sum(x.startswith('M-') for x in ids), 18)

class InventoryTests(unittest.TestCase):
    def test_inventory_does_not_follow_symlinks_or_execute(self):
        base = Path(os.environ.get('TMPDIR', str(Path.home())))
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            root = Path(folder); (root/'src').mkdir(); (root/'src'/'operator.go').write_text('package x')
            (root/'vendor').mkdir(); (root/'vendor'/'skip.go').write_text('package skip')
            (root/'Makefile').write_text('all:\n\ttouch SHOULD_NOT_EXIST\n')
            (root/'link.go').symlink_to(root/'src'/'operator.go')
            r = inv.inventory(root)
            self.assertEqual(set(r['candidate_paths']), {'src/operator.go','Makefile'})
            self.assertFalse((root/'SHOULD_NOT_EXIST').exists())
            self.assertIn('link.go',r['excluded_paths'])

    def test_missing_repo(self):
        with self.assertRaises(ValueError):
            inv.inventory(HERE / 'definitely-missing-repo')

if __name__ == '__main__':
    unittest.main(verbosity=2)
