#!/usr/bin/env python3
"""Validate coverage/report structure, NOT evidence truth or operator correctness. Python 3.9+."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r'(?m)^#{2,4}\s+(B\d{2}-\d{2}|M-\d{2})\b')
STATES = {'pass', 'fail', 'unknown', 'not_applicable'}


def catalog(root=ROOT):
    refs = Path(root) / 'references'
    files = [refs / ('ch%02d.md' % n) for n in range(1, 12)] + [refs / 'modern-checks.md']
    ids = []
    for path in files:
        text = path.read_text(encoding='utf-8')
        found = ID.findall(text)
        if not found:
            raise ValueError('no check headings in ' + str(path))
        ids.extend(found)
    duplicates = [x for x, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError('duplicate catalog IDs: ' + ', '.join(duplicates))
    return ids


def text(value):
    return isinstance(value, str) and bool(value.strip())


def evidence(value):
    return isinstance(value, list) and bool(value) and all(text(x) for x in value)


def validate(doc, expected):
    errors = []
    if not isinstance(doc, dict):
        return ['report must be an object']
    scope = doc.get('scope')
    if not isinstance(scope, dict):
        errors.append('scope must be an object')
    else:
        for key in ('repository', 'revision'):
            if not text(scope.get(key)):
                errors.append('scope.' + key + ' required')
        if scope.get('mode') not in {'full', 'targeted'}:
            errors.append('scope.mode must be full or targeted')
        if not isinstance(scope.get('limitations'), list) or not all(text(x) for x in scope['limitations']):
            errors.append('scope.limitations must be an array of strings')
    checks = doc.get('checks')
    if not isinstance(checks, list):
        return errors + ['checks must be an array']
    seen, failed = [], set()
    for i, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append('check %d must be an object' % i)
            continue
        key, status = check.get('id'), check.get('status')
        if not text(key):
            errors.append('check ID required')
            continue
        seen.append(key)
        if status not in STATES:
            errors.append(key + ': invalid status')
        if not text(check.get('reason')):
            errors.append(key + ': reason required')
        if status in {'pass', 'fail'} and not evidence(check.get('evidence')):
            errors.append(key + ': pass/fail requires evidence')
        if status == 'fail':
            failed.add(key)
    expected = set(expected)
    if set(seen) != expected:
        errors.append('coverage mismatch; missing=%s extra=%s' % (sorted(expected-set(seen)), sorted(set(seen)-expected)))
    if len(seen) != len(set(seen)):
        errors.append('duplicate check IDs')
    findings = doc.get('findings')
    linked, finding_ids = set(), []
    if not isinstance(findings, list):
        errors.append('findings must be an array')
    else:
        for f in findings:
            if not isinstance(f, dict):
                errors.append('finding must be an object')
                continue
            for key in ('id', 'title', 'location', 'scenario', 'remediation', 'verification'):
                if not text(f.get(key)):
                    errors.append('finding.' + key + ' required')
            if text(f.get('id')):
                finding_ids.append(f['id'])
            if f.get('check_id') not in expected:
                errors.append('finding check_id not in catalog')
            else:
                linked.add(f['check_id'])
            if f.get('severity') not in {'critical', 'high', 'medium', 'low', 'info'}:
                errors.append('invalid severity')
            if f.get('confidence') not in {'confirmed', 'probable', 'needs_validation'}:
                errors.append('invalid confidence')
            if not evidence(f.get('evidence')):
                errors.append('finding evidence required')
    if len(finding_ids) != len(set(finding_ids)):
        errors.append('duplicate finding IDs')
    if failed-linked:
        errors.append('failed checks without findings: ' + ', '.join(sorted(failed-linked)))
    tests = doc.get('tests')
    if not isinstance(tests, list):
        errors.append('tests must be an array')
    else:
        for t in tests:
            if not isinstance(t, dict):
                errors.append('test must be an object')
                continue
            if not text(t.get('command')) or not text(t.get('environment')):
                errors.append('test command/environment required')
            status = t.get('status')
            if status == 'not_run':
                if not text(t.get('reason')):
                    errors.append('not_run test needs reason')
            elif status in {'passed', 'failed'}:
                code = t.get('exit_code')
                if type(code) is not int or (status == 'passed' and code != 0) or (status == 'failed' and code == 0):
                    errors.append('test exit code contradicts status')
                if not text(t.get('artifact')):
                    errors.append('executed test artifact required')
            else:
                errors.append('invalid test status')
    return errors


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', nargs='?')
    p.add_argument('--list-checks', action='store_true')
    args = p.parse_args()
    try:
        ids = catalog()
        if args.list_checks:
            print(json.dumps({'count': len(ids), 'ids': ids}, indent=2))
            return 0
        if not args.report:
            p.error('report path or --list-checks required')
        doc = json.loads(Path(args.report).read_text(encoding='utf-8'))
        errors = validate(doc, ids)
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({'valid': False, 'errors': [str(error)]}))
        return 2
    print(json.dumps({'valid': not errors, 'catalog_checks': len(ids), 'errors': errors,
                      'meaning': 'Structure and coverage only; not a correctness certificate'}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
