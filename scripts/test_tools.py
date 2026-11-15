#!/usr/bin/env python3
"""Synthetic tool tests; do not claim Kubernetes integration coverage."""
import copy
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

v = load('validate_report')
inv = load('inventory')

class ReportTests(unittest.TestCase):
    def base(self):
        return {'scope': {'repository': 'synthetic-fixture', 'revision': 'fixture-v1', 'mode': 'full', 'completion': 'incomplete', 'limitations': ['Static test only']},
                'checks': [{'id': 'M-01', 'status': 'unknown', 'reason': 'No implementation supplied', 'evidence': [],
                            'resolution': {'category': 'not_inspected', 'inspected_evidence': [],
                                           'missing_requirement': 'Implementation inspection',
                                           'next_action': 'Read the controller and its tests'}}],
                'findings': [], 'tests': []}

    def test_unknown_is_honest(self):
        d = self.base()
        d['scope']['completion'] = 'incomplete'
        d['checks'][0]['resolution'] = {
            'category': 'not_inspected', 'inspected_evidence': [],
            'missing_requirement': 'Implementation inspection',
            'next_action': 'Read the controller and its tests',
        }
        self.assertEqual(v.validate(d, ['M-01']), [])
        del d['checks'][0]['resolution']
        self.assertTrue(v.validate(d, ['M-01']))

    def test_completion_gates(self):
        for completion in ('incomplete', 'blocked', 'complete', None, 'full'):
            for category in ('not_inspected', 'missing_artifact', 'requires_runtime'):
                with self.subTest(completion=completion, category=category):
                    d = self.base()
                    d['scope']['completion'] = completion
                    d['checks'][0]['resolution'].update(
                        category=category, inspected_evidence=['inventory.json: source absent'])
                    valid = completion == 'incomplete' or (
                        completion == 'blocked' and category != 'not_inspected')
                    self.assertEqual(not v.validate(d, ['M-01']), valid)
        d = self.base()
        d['checks'][0].update(status='pass', evidence=['controller.go:1-9'])
        d['scope']['completion'] = 'complete'
        self.assertEqual(v.validate(d, ['M-01']), [])
        d['scope']['completion'] = 'blocked'
        self.assertTrue(v.validate(d, ['M-01']))

    def test_targeted_scope(self):
        d = self.base()
        d['scope'].update(mode='targeted', completion='complete', check_ids=['M-02'])
        d['checks'][0]['resolution']['category'] = 'out_of_scope'
        d['checks'].append({'id': 'M-02', 'status': 'pass', 'reason': 'Inspected',
                            'evidence': ['controller.go:1-9']})
        self.assertEqual(v.validate(d, ['M-01', 'M-02']), [])
        for ids in (None, [], ['M-01'], ['M-02', 'M-02'], ['unknown'], [{}]):
            with self.subTest(ids=ids):
                bad = copy.deepcopy(d)
                bad['scope']['check_ids'] = ids
                self.assertTrue(v.validate(bad, ['M-01', 'M-02']))
        d['scope']['mode'] = 'full'
        self.assertTrue(v.validate(d, ['M-01', 'M-02']))

    def test_blocker_requires_details(self):
        d = self.base()
        d['scope']['completion'] = 'blocked'
        d['checks'][0]['resolution'].update(category='missing_artifact',
                                           inspected_evidence=['inventory.json: missing chart'])
        self.assertEqual(v.validate(d, ['M-01']), [])
        for field in ('category', 'inspected_evidence', 'missing_requirement', 'next_action'):
            bad = copy.deepcopy(d)
            del bad['checks'][0]['resolution'][field]
            self.assertTrue(v.validate(bad, ['M-01']))

    def test_missing_coverage(self):
        self.assertTrue(v.validate(self.base(), ['M-01', 'M-02']))

    def test_pass_without_evidence(self):
        d = self.base()
        d['checks'][0]['status'] = 'pass'
        self.assertTrue(v.validate(d, ['M-01']))

    def test_evidenced_static_pass(self):
        d = self.base()
        d['checks'][0].update(status='pass', evidence=['fixture.go:1-9: deterministic pure transformation'])
        self.assertEqual(v.validate(d, ['M-01']), [])

    def test_fail_without_finding(self):
        d = self.base()
        d['checks'][0].update(status='fail', evidence=['fixture.go:1'])
        self.assertTrue(v.validate(d, ['M-01']))

    def test_na_requires_reason(self):
        d = self.base()
        d['checks'][0].update(status='not_applicable', reason='')
        self.assertTrue(v.validate(d, ['M-01']))

    def test_duplicate_check(self):
        d = self.base()
        d['checks'].append(copy.deepcopy(d['checks'][0]))
        self.assertTrue(v.validate(d, ['M-01']))

    def test_false_test_result(self):
        d = self.base()
        d['tests'] = [{'command':'test', 'environment':'fixture', 'status':'passed', 'exit_code':1, 'artifact':'log'}]
        self.assertTrue(v.validate(d, ['M-01']))

    def test_bad_document_types(self):
        for d in (None, [], {'checks': [None], 'tests': [None], 'findings': [None]}):
            self.assertTrue(v.validate(d, ['M-01']))

    def finding(self):
        return {'id': 'F-1', 'check_ids': ['M-01', 'M-02'], 'severity': 'high',
                'title': 'Shared defect', 'location': 'controller.go:1',
                'scenario': 'Retry after restart', 'remediation': 'Persist identity',
                'verification': 'Replay test', 'confidence': 'confirmed',
                'evidence': ['controller.go:1: duplicate allocation']}

    def test_deduplicated_finding_links_all_failures(self):
        d = self.base()
        d['scope']['completion'] = 'complete'
        d['checks'] = [{'id': key, 'status': 'fail', 'reason': 'Shared defect',
                        'evidence': ['controller.go:1']} for key in ('M-01', 'M-02')]
        d['findings'] = [self.finding()]
        self.assertEqual(v.validate(d, ['M-01', 'M-02']), [])
        for ids in ([], ['M-01'], ['M-01', 'bogus'], ['M-01', 'M-01'], [{}]):
            d['findings'][0]['check_ids'] = ids
            self.assertTrue(v.validate(d, ['M-01', 'M-02']))
        d['checks'].pop()
        d['findings'][0].pop('check_ids')
        d['findings'][0]['check_id'] = 'M-01'
        self.assertEqual(v.validate(d, ['M-01']), [])

    def test_malformed_fields_return_diagnostics(self):
        fields = [('scope', 'mode'), ('scope', 'completion'), ('checks', 'id'),
                  ('checks', 'status'), ('findings', 'check_id'), ('findings', 'check_ids'),
                  ('findings', 'severity'), ('findings', 'confidence'), ('tests', 'status')]
        for section, field in fields:
            for value in ([], {}, None, 42):
                with self.subTest(section=section, field=field, value=value):
                    d = self.base()
                    d['findings'] = [self.finding()]
                    d['findings'][0]['check_ids'] = ['M-01']
                    d['tests'] = [{'command': 'test', 'environment': 'fixture',
                                   'status': 'not_run', 'reason': 'Static only'}]
                    target = d[section] if section == 'scope' else d[section][0]
                    if field == 'check_id':
                        target.pop('check_ids')
                    target[field] = value
                    self.assertTrue(v.validate(d, ['M-01']))
        for value in ([], {}, None, 42):
            d = self.base()
            d['checks'][0]['resolution']['category'] = value
            self.assertTrue(v.validate(d, ['M-01']))

    def test_complete_catalog(self):
        ids = v.catalog()
        self.assertEqual(len(ids), 88)
        self.assertEqual(len(ids), len(set(ids)))
        for n in range(1, 12):
            self.assertTrue(any(x.startswith('B%02d-' % n) for x in ids))
        self.assertEqual(sum(x.startswith('M-') for x in ids), 18)

class InventoryTests(unittest.TestCase):
    def test_inventory_does_not_follow_symlinks_or_execute(self):
        base = Path(os.environ.get('TMPDIR', str(Path.home())))
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            root = Path(folder)
            (root/'src').mkdir()
            (root/'src'/'operator.go').write_text('package x')
            (root/'vendor').mkdir()
            (root/'vendor'/'skip.go').write_text('package skip')
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
