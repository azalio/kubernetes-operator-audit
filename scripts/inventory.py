#!/usr/bin/env python3
"""Read-only path inventory, not a compliance scanner. Python 3.9+, stdlib only."""
import argparse
import json
import os
from pathlib import Path

EXCLUDE = {'.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', 'vendor', '__pycache__', 'target', 'dist', 'build'}
SUFFIXES = {'.go', '.py', '.rs', '.java', '.yaml', '.yml', '.json', '.toml', '.md', '.sh'}
NAMES = {'Dockerfile', 'Containerfile', 'Makefile', 'PROJECT', 'go.mod', 'go.sum', 'Chart.yaml', 'requirements.txt', 'pom.xml'}


def inventory(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('repository must be an existing directory')
    paths, skipped, errors = [], [], []
    def onerror(error):
        errors.append(str(error))
    for base, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        keep = []
        for name in sorted(dirs):
            p = Path(base) / name
            if name in EXCLUDE or p.is_symlink():
                skipped.append(str(p.relative_to(root)))
            else:
                keep.append(name)
        dirs[:] = keep
        for name in sorted(files):
            p = Path(base) / name
            if p.is_symlink():
                skipped.append(str(p.relative_to(root)))
                continue
            if p.suffix in SUFFIXES or name in NAMES or name.startswith(('Dockerfile.', 'Containerfile.')):
                paths.append(str(p.relative_to(root)))
    return {'repository': str(root), 'candidate_count': len(paths), 'candidate_paths': paths,
            'excluded_paths': skipped, 'read_errors': errors,
            'limitations': ['Names only; no semantic verdict', 'Excluded generated/build/vendor directories may need explicit inspection',
                            'No repository scripts executed; no cluster contacted; no symlinks followed']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('repository')
    args = p.parse_args()
    try:
        result = inventory(args.repository)
    except (OSError, ValueError) as error:
        p.exit(2, str(error) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result['read_errors'] else 0)
