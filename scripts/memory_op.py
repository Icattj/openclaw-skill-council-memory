#!/usr/bin/env python3
"""
council-memory: memory_op.py
Read, write, search, and inject Council Room persistent memory.
"""
import argparse, json, os, sys
from datetime import datetime
from pathlib import Path

WORKSPACE   = Path('/home/openclaw/.openclaw/workspace')
VAULT       = Path('/home/openclaw/livesync-bridge/vault')
MEMORY_MD   = WORKSPACE / 'MEMORY.md'
COUNCIL_MEM = Path('/home/openclaw/council-room/data/council_memory.json')
DAILY_DIR   = WORKSPACE / 'memory'

def today():
    return datetime.now().strftime('%Y-%m-%d')

def load_council_mem():
    if COUNCIL_MEM.exists():
        with open(COUNCIL_MEM) as f:
            return json.load(f)
    return {'facts': [], 'decisions': [], 'kpis': {}, 'lessons': []}

def save_council_mem(data):
    COUNCIL_MEM.parent.mkdir(parents=True, exist_ok=True)
    with open(COUNCIL_MEM, 'w') as f:
        json.dump(data, f, indent=2)

def op_read(args):
    """Print a summary of long-term memory."""
    out = []
    if MEMORY_MD.exists():
        content = MEMORY_MD.read_text()
        # Print first 3000 chars
        out.append('=== MEMORY.md (first 3000 chars) ===')
        out.append(content[:3000])
    data = load_council_mem()
    if data.get('facts'):
        out.append('\n=== Council Facts ===')
        for f in data['facts'][-10:]:
            text = f.get('text') or f"{f.get('entity','?')}: {f.get('value','?')}"
            out.append(f"  • {text[:100]} [{f.get('date',f.get('ts','?'))}]")
    if data.get('decisions'):
        out.append('\n=== Recent Decisions ===')
        for d in data['decisions'][-5:]:
            text = d.get('text') or d.get('value','?')
            out.append(f"  ✅ {text[:100]} [{d.get('date',d.get('ts','?'))}]")
    if data.get('kpis'):
        out.append('\n=== KPIs ===')
        for k, v in data['kpis'].items():
            out.append(f"  📊 {k}: {v}")
    print('\n'.join(out))

def op_write(args):
    """Write a fact or decision to council memory."""
    data = load_council_mem()
    entry = {'text': args.fact, 'date': today(), 'category': args.category}
    category = args.category or 'facts'
    # Adapt entry to actual schema (entity/value style for facts)
    fact_entry = {'entity': args.category, 'value': args.fact,
                  'type': args.category, 'ts': today(), 'text': args.fact,
                  'date': today(), 'agent': 'michael'}
    if category == 'decisions':
        data.setdefault('decisions', []).append(fact_entry)
    elif category == 'kpi':
        if ':' in args.fact:
            k, v = args.fact.split(':', 1)
            data.setdefault('kpis', {})[k.strip()] = v.strip()
        else:
            data.setdefault('kpis', {})[args.fact] = today()
    elif category == 'lesson':
        data.setdefault('lessons', []).append(fact_entry)
    else:
        data.setdefault('facts', []).append(fact_entry)
    data['lastUpdated'] = datetime.now().isoformat()
    save_council_mem(data)
    print(f"✅ Saved to council_memory.json [{category}]: {args.fact[:80]}")

def op_search(args):
    """Search memory for a query string."""
    query = args.query.lower()
    results = []
    # Search MEMORY.md
    if MEMORY_MD.exists():
        lines = MEMORY_MD.read_text().splitlines()
        for i, line in enumerate(lines):
            if query in line.lower():
                results.append(f"MEMORY.md:{i+1}: {line.strip()}")
    # Search council_memory.json
    data = load_council_mem()
    for cat in ['facts', 'decisions', 'lessons']:
        for entry in data.get(cat, []):
            if query in entry.get('text','').lower():
                results.append(f"council_mem[{cat}]: {entry['text']} [{entry.get('date','?')}]")
    # Search recent daily notes
    if DAILY_DIR.exists():
        for f in sorted(DAILY_DIR.glob('*.md'))[-7:]:
            lines = f.read_text().splitlines()
            for i, line in enumerate(lines):
                if query in line.lower():
                    results.append(f"{f.name}:{i+1}: {line.strip()}")
    if results:
        print(f"🔍 Found {len(results)} results for '{args.query}':")
        for r in results[:20]:
            print(f"  {r}")
    else:
        print(f"🔍 No results for '{args.query}'")

def op_daily(args):
    """Append a note to today's daily memory file."""
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    daily_file = DAILY_DIR / f'{today()}.md'
    timestamp = datetime.now().strftime('%H:%M')
    entry = f"\n- [{timestamp}] {args.note}"
    with open(daily_file, 'a') as f:
        f.write(entry)
    print(f"✅ Appended to {daily_file.name}: {args.note[:80]}")

def op_context(args):
    """Generate context string to inject into agent prompts."""
    parts = []
    # Core identity from MEMORY.md
    if MEMORY_MD.exists():
        content = MEMORY_MD.read_text()
        # Extract "Who Lucy Is" section
        if '## Who Lucy Is' in content:
            section = content.split('## Who Lucy Is')[1].split('##')[0].strip()
            parts.append(f"[CONTEXT: Who you're talking to]\n{section[:400]}")
        # Extract DataFlow Mission
        if '## DataFlow Mission' in content:
            section = content.split('## DataFlow Mission')[1].split('##')[0].strip()
            parts.append(f"\n[CONTEXT: The Mission]\n{section[:300]}")
    # Recent decisions
    data = load_council_mem()
    if data.get('decisions'):
        recent = data['decisions'][-3:]
        parts.append('\n[CONTEXT: Recent Decisions]')
        for d in recent:
            parts.append(f"  • {d['text']} ({d.get('date','?')})")
    # KPIs
    if data.get('kpis'):
        parts.append('\n[CONTEXT: Current KPIs]')
        for k, v in list(data['kpis'].items())[:5]:
            parts.append(f"  • {k}: {v}")
    # Today's notes
    today_file = DAILY_DIR / f'{today()}.md'
    if today_file.exists():
        content = today_file.read_text().strip()
        if content:
            parts.append(f"\n[CONTEXT: Today's Notes]\n{content[-500:]}")
    context_str = '\n'.join(parts)
    print(context_str if context_str else '[No memory context found — run memory_op.py write first]')

def main():
    parser = argparse.ArgumentParser(description='Council Room Memory Operations')
    sub = parser.add_subparsers(dest='op')

    # read
    sub.add_parser('read', help='Print memory summary')

    # write
    wp = sub.add_parser('write', help='Write a fact/decision')
    wp.add_argument('--fact', required=True, help='The fact to store')
    wp.add_argument('--category', default='facts',
                    choices=['facts','decisions','kpi','lesson'],
                    help='Memory category')

    # search
    sp = sub.add_parser('search', help='Search memory')
    sp.add_argument('--query', required=True, help='Search query')

    # daily
    dp = sub.add_parser('daily', help='Append to daily notes')
    dp.add_argument('--note', required=True, help='Note to append')

    # context
    cp = sub.add_parser('context', help='Generate agent context string')
    cp.add_argument('--agent', default='all', help='Agent ID (optional)')

    args = parser.parse_args()
    ops = {'read': op_read, 'write': op_write, 'search': op_search,
           'daily': op_daily, 'context': op_context}
    if args.op in ops:
        ops[args.op](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
