# -*- coding: utf-8 -*-
import sys, io, json, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

demo = os.path.join(os.path.dirname(__file__))
parent = os.path.dirname(demo)
os.chdir(parent)

for d in sorted(os.listdir(demo)):
    if d.startswith('.'):
        continue
    jpath = os.path.join(demo, d, f'{d}.json')
    if not os.path.exists(jpath):
        print(f'{d}: no json')
        continue
    with open(jpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    pages = data.get('pages', [])
    print(f'=== {d} ===')
    print(f'  title: {data.get("title","")}')
    print(f'  subtitle: {data.get("subtitle","")}')
    print(f'  pages: {len(pages)}')
    if pages:
        for p in pages[:3]:
            tasks = p.get('tasks', [])
            inst = p.get('instruction','')
            print(f'  p.{p["page_number"]}: t={p["page_type"]} inst="{inst[:60]}" tasks={len(tasks)}')
            for t in tasks[:2]:
                q = t["question"][:80]
                a = t.get("answer","")
                print(f'    Q: {q}')
                if a:
                    print(f'    A: {str(a)[:60]}')
        if len(pages) > 3:
            print(f'  ... +{len(pages)-3} more')
    qc = data.get('_quality', {})
    if qc:
        errs = qc.get("errors", [])
        warns = qc.get("warnings", [])
        print(f'  quality: passed={qc.get("passed")} errors={errs} warnings={len(warns)}')
    print()

# diversity check
type_counts = {}
for d in sorted(os.listdir(demo)):
    if d.startswith('.'):
        continue
    jpath = os.path.join(demo, d, f'{d}.json')
    if not os.path.exists(jpath):
        continue
    with open(jpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for p in data.get('pages', []):
        pt = p.get('page_type', 'unknown')
        type_counts[pt] = type_counts.get(pt, 0) + 1
print('=== Card type diversity ===')
for k, v in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')
print(f'Total unique types: {len(type_counts)}')

# Instruction repetition
print('\n=== Instruction repetition check ===')
repetitive = False
for d in sorted(os.listdir(demo)):
    if d.startswith('.'):
        continue
    jpath = os.path.join(demo, d, f'{d}.json')
    if not os.path.exists(jpath):
        continue
    with open(jpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    insts = [p.get('instruction','') for p in data.get('pages', []) if p.get('instruction')]
    unique = len(set(insts))
    status = 'OK' if unique == len(insts) else f'REPETITION ({len(insts)} inst, {unique} unique)'
    if unique < len(insts):
        repetitive = True
    print(f'  {d}: {status}')
print(f'Repetition found: {"YES" if repetitive else "NO"}')
