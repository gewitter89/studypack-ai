import json, os

demo = 'max_quality_demo'
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
                print(f'    Q: {t["question"][:80]}')
                if t.get('answer'):
                    print(f'    A: {t["answer"][:60]}')
        if len(pages) > 3:
            print(f'  ... +{len(pages)-3} more')
    qc = data.get('_quality', {})
    if qc:
        print(f'  quality: passed={qc.get("passed")} errors={qc.get("errors")} warnings={qc.get("warnings")}')
    print()

# diversity check: count unique card types across all 12
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
print(f'  Total unique types: {len(type_counts)}')
print()

# Check for repetitive instructions across all pages
print('=== Instruction repetition check ===')
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
    if unique < len(insts):
        print(f'  {d}: {len(insts)} instructions, only {unique} unique')
    else:
        print(f'  {d}: {len(insts)} instructions, all unique OK')
