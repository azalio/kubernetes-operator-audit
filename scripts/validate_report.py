#!/usr/bin/env python3
"""Validate coverage/report structure, NOT evidence truth or operator correctness. Python 3.9+."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r'(?m)^#{2,4}\s+(B\d{2}-\d{2}|M-\d{2})\b')
STATES = ('pass', 'fail', 'unknown', 'not_applicable')


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
    expected = set(expected)
    completion, mode, in_scope = None, None, expected
    blockers = []
    scope = doc.get('scope')
    if not isinstance(scope, dict):
        errors.append('scope must be an object')
    else:
        for key in ('repository', 'revision'):
            if not text(scope.get(key)):
                errors.append('scope.' + key + ' required')
        mode, completion = scope.get('mode'), scope.get('completion')
        if mode not in ('full', 'targeted'):
            errors.append('scope.mode must be full or targeted')
        if completion not in ('incomplete', 'blocked', 'complete'):
            errors.append('scope.completion must be incomplete, blocked or complete')
        if mode == 'targeted':
            ids = scope.get('check_ids')
            if not isinstance(ids, list) or not evidence(ids) or len(set(ids)) != len(ids) or not set(ids) <= expected:
                errors.append('scope.check_ids must be a nonempty array of unique catalog IDs')
            else:
                in_scope = set(ids)
        if not isinstance(scope.get('limitations'), list) or not all(text(x) for x in scope['limitations']):
            errors.append('scope.limitations must be an array of strings')
    checks = doc.get('checks')
    if not isinstance(checks, list):
        return errors + ['checks must be an array']
    seen, failed, check_states = [], set(), {}
    for i, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append('check %d must be an object' % i)
            continue
        key, status = check.get('id'), check.get('status')
        if not isinstance(key, str) or not key.strip():
            errors.append('check ID required')
            continue
        seen.append(key)
        check_states[key] = status
        if status not in STATES:
            errors.append(key + ': invalid status')
        if not text(check.get('reason')):
            errors.append(key + ': reason required')
        if status in ('pass', 'fail') and not evidence(check.get('evidence')):
            errors.append(key + ': pass/fail requires evidence')
        if status == 'unknown':
            resolution = check.get('resolution')
            if not isinstance(resolution, dict):
                errors.append(key + ': unknown requires resolution object')
            else:
                if resolution.get('category') not in ('not_inspected', 'missing_artifact', 'requires_runtime', 'out_of_scope'):
                    errors.append(key + ': invalid resolution category')
                inspected = resolution.get('inspected_evidence')
                if not isinstance(inspected, list) or not all(text(x) for x in inspected):
                    errors.append(key + ': inspected_evidence must be an array of strings')
                for field in ('missing_requirement', 'next_action'):
                    if not text(resolution.get(field)):
                        errors.append(key + ': resolution.' + field + ' required')
                category = resolution.get('category')
                if category in ('missing_artifact', 'requires_runtime'):
                    if not evidence(inspected):
                        errors.append(key + ': blocker requires inspected evidence')
                    if key in in_scope:
                        blockers.append(key)
                if category == 'out_of_scope' and (mode != 'targeted' or key in in_scope):
                    errors.append(key + ': out_of_scope requires targeted scope excluding this ID')
                if completion in ('blocked', 'complete') and category == 'not_inspected':
                    errors.append(key + ': not_inspected prevents blocked/complete')
            if completion == 'complete' and key in in_scope:
                errors.append(key + ': in-scope unknown prevents complete')
        if key not in in_scope and (status != 'unknown' or not isinstance(check.get('resolution'), dict)
                                    or check['resolution'].get('category') != 'out_of_scope'):
            errors.append(key + ': excluded check must be unknown/out_of_scope')
        if status == 'fail':
            failed.add(key)
    if completion == 'blocked' and not blockers:
        errors.append('blocked requires an in-scope missing_artifact or requires_runtime unknown')
    if set(seen) != expected:
        errors.append('coverage mismatch; missing=%s extra=%s' % (sorted(expected-set(seen)), sorted(set(seen)-expected)))
    if len(seen) != len(set(seen)):
        errors.append('duplicate check IDs')
    findings = doc.get('findings')
    confirmed_links, finding_ids = set(), []
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
            severity, confidence = f.get('severity'), f.get('confidence')
            is_defect = severity in ('critical', 'high', 'medium', 'low') and confidence == 'confirmed'
            is_risk = severity in ('critical', 'high', 'medium', 'low') and confidence in ('probable', 'needs_validation')
            ids = f.get('check_ids') if 'check_ids' in f else [f.get('check_id')]
            if not isinstance(ids, list) or not evidence(ids) or len(set(ids)) != len(ids) or not set(ids) <= expected:
                errors.append('finding check_ids must contain unique catalog IDs')
            else:
                for key in ids:
                    status = check_states.get(key)
                    if key not in in_scope:
                        errors.append(f'{key}: finding must link an in-scope check')
                    if status == 'not_applicable':
                        errors.append(f'{key}: finding cannot link a not_applicable check')
                    if is_defect and status != 'fail':
                        errors.append(f'{key}: confirmed defect requires fail status')
                    if is_risk and status not in ('unknown', 'fail'):
                        errors.append(f'{key}: risk requires unknown or independently confirmed fail status')
                if is_defect:
                    confirmed_links.update(ids)
            if 'check_ids' in f and 'check_id' in f:
                errors.append('finding must use check_ids or check_id, not both')
            if severity not in ('critical', 'high', 'medium', 'low', 'info'):
                errors.append('invalid severity')
            if confidence not in ('confirmed', 'probable', 'needs_validation'):
                errors.append('invalid confidence')
            if not evidence(f.get('evidence')):
                errors.append('finding evidence required')
    if len(finding_ids) != len(set(finding_ids)):
        errors.append('duplicate finding IDs')
    if failed-confirmed_links:
        errors.append('failed checks without confirmed defects: ' + ', '.join(sorted(failed-confirmed_links)))
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
            elif status in ('passed', 'failed'):
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
