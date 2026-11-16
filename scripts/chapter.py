#!/usr/bin/env python3
"""Route isolated chapter reviews and validate partial reports; no repository execution."""
import argparse
import json
from pathlib import Path
import re

import validate_report as report

ROOT = Path(__file__).resolve().parents[1]
MODERN = {
    1: (), 2: (10, 11), 3: (1, 4, 6), 4: (2, 3, 17),
    5: (7, 12, 13), 6: (16,), 7: (), 8: (8, 9),
    9: (18,), 10: (5,), 11: (14, 15),
}


def check_ids(chapter, root=ROOT):
    if chapter not in MODERN:
        raise ValueError('chapter must be between 1 and 11')
    ids = report.catalog(root)
    prefix = 'B%02d-' % chapter
    modern = ['M-%02d' % n for n in MODERN[chapter]]
    if not set(modern) <= set(ids):
        raise ValueError('chapter mapping references missing checks')
    return [key for key in ids if key.startswith(prefix)] + modern


def plan(root=ROOT):
    chapters = [{'chapter': n, 'reference': 'references/ch%02d.md' % n,
                 'check_ids': check_ids(n, root)} for n in range(1, 12)]
    owned = [key for chapter in chapters for key in chapter['check_ids']]
    if len(owned) != len(set(owned)) or set(owned) != set(report.catalog(root)):
        raise ValueError('chapter assignment must cover the catalog exactly once')
    return {'chapters': chapters, 'default_order': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 9],
            'parallel_after': 1, 'synthesis_chapter': 9}


def context(chapter, root=ROOT):
    ids = check_ids(chapter, root)
    refs = Path(root) / 'references'
    chapter_text = (refs / ('ch%02d.md' % chapter)).read_text(encoding='utf-8')
    modern_text = (refs / 'modern-checks.md').read_text(encoding='utf-8')
    sections = re.split(r'(?m)(?=^## M-\d{2}\b)', modern_text)
    selected = [section for section in sections[1:]
                if report.ID.findall(section)[0] in ids]
    header = ('Assigned chapter: %02d\nAssigned check IDs: %s\n'
              'This is one chapter context, not a full audit. Follow chapter-workflow.md.\n\n'
              % (chapter, ', '.join(ids)))
    supplement = '\n\n' + sections[0] + '\n'.join(selected) if selected else ''
    return header + chapter_text + supplement


def validate(doc, chapter, root=ROOT):
    errors = report.validate(doc, check_ids(chapter, root))
    scope = doc.get('scope') if isinstance(doc, dict) else None
    if not isinstance(scope, dict) or scope.get('mode') != 'targeted':
        errors.append('chapter report requires scope.mode=targeted')
    if not isinstance(scope, dict) or type(scope.get('chapter')) is not int or scope['chapter'] != chapter:
        errors.append('scope.chapter must match the requested chapter')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('plan', help='List chapter ownership without loading rule text')
    for name in ('context', 'validate'):
        command = commands.add_parser(name)
        command.add_argument('chapter', type=int, choices=range(1, 12))
        if name == 'validate':
            command.add_argument('report')
    args = parser.parse_args()
    try:
        if args.command == 'plan':
            print(json.dumps(plan(), indent=2))
        elif args.command == 'context':
            print(context(args.chapter))
        else:
            doc = json.loads(Path(args.report).read_text(encoding='utf-8'))
            errors = validate(doc, args.chapter)
            print(json.dumps({'valid': not errors, 'chapter': args.chapter,
                              'chapter_checks': len(check_ids(args.chapter)), 'errors': errors,
                              'meaning': 'Partial report structure only; not a full audit or proof of context isolation'},
                             indent=2))
            return 1 if errors else 0
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({'valid': False, 'errors': [str(error)]}))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
