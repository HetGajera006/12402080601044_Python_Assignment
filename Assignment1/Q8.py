import os
import pickle
import re
import sys
import zipfile
TOKEN_RE = re.compile('[a-z0-9_]+')
MAX_TOKEN = 50

def build(folder, zip_name):
    if not os.path.isdir(folder):
        sys.exit(f'Folder not found: {folder}')
    zip_abs = os.path.abspath(zip_name)
    paths = []
    for root, _, names in os.walk(folder):
        for nm in names:
            full = os.path.join(root, nm)
            if os.path.abspath(full) != zip_abs:
                paths.append(full)
    paths.sort()
    index, total_lines, total_files = ({}, 0, 0)
    used = []
    for path in paths:
        rel = os.path.relpath(path, folder).replace(os.sep, '/')
        try:
            with open(path, encoding='utf-8', errors='replace') as fh:
                for ln, line in enumerate(fh, 1):
                    total_lines += 1
                    for tok in set(TOKEN_RE.findall(line.lower())):
                        if len(tok) <= MAX_TOKEN:
                            index.setdefault(tok, []).append((rel, ln))
        except OSError as exc:
            print(f'Skipping {path}: {exc}', file=sys.stderr)
            continue
        total_files += 1
        used.append((path, rel))
    stem = zip_name[:-4] if zip_name.lower().endswith('.zip') else zip_name
    pkl_path = stem + '_index.pkl'
    with open(pkl_path, 'wb') as fh:
        pickle.dump(index, fh, protocol=pickle.HIGHEST_PROTOCOL)
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path, rel in used:
            zf.write(path, 'logs/' + rel)
        zf.write(pkl_path, 'index.pkl')
    print(f'FILES {total_files}')
    print(f'LINES {total_lines}')
    print(f'TOKENS {len(index)}')

def search(pkl_path, queries):
    try:
        with open(pkl_path, 'rb') as fh:
            index = pickle.load(fh)
    except (OSError, pickle.UnpicklingError, EOFError) as exc:
        sys.exit(f'Cannot load index: {exc}')
    for q in queries:
        tok = q.lower().strip()
        print(f'{tok}:')
        hits = index.get(tok, [])
        if not hits:
            print('  (no matches)')
        for fname, ln in hits:
            print(f'  {fname}:{ln}')

def main():
    words = sys.argv[1:] or sys.stdin.read().split()
    if not words:
        sys.exit('Usage: BUILD folder out.zip | SEARCH index.pkl tokens...')
    mode = words[0].upper()
    if mode == 'BUILD' and len(words) >= 3:
        build(words[1], words[2])
    elif mode == 'SEARCH' and len(words) >= 3:
        rest = words[2:]
        if rest[0].isdigit() and len(rest) - 1 == int(rest[0]):
            rest = rest[1:]
        search(words[1], rest)
    else:
        sys.exit('Usage: BUILD folder out.zip | SEARCH index.pkl tokens...')
if __name__ == '__main__':
    main()
