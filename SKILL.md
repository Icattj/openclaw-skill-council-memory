---
name: council-memory
description: "Persistent memory layer for Council Room — reads, writes, and searches agent memory across sessions. Use when saving important decisions/facts to long-term memory, recalling past sessions, updating MEMORY.md or daily notes, searching the Obsidian vault for context, or injecting memory into agent prompts so agents never forget who Lucy is or what DataFlow is building. Replaces the goldfish memory problem."
---

# Council Memory Skill

Gives Council Room agents persistent memory across sessions — like Kora's shared memory, but self-hosted and unlimited.

## Memory Architecture

```
Short-term  → memory/YYYY-MM-DD.md      (daily raw notes)
Long-term   → MEMORY.md                  (curated facts)
Agent facts → vault/00_System_Core/      (Obsidian vault)
Council KB  → council_memory.json        (shared agent facts)
```

**Paths:**
- Workspace: `/home/openclaw/.openclaw/workspace/`
- Vault: `/home/openclaw/livesync-bridge/vault/`
- Council memory file: `/home/openclaw/council-room/data/council_memory.json`
- Daily notes: `/home/openclaw/.openclaw/workspace/memory/YYYY-MM-DD.md`

## Core Operations

### Read Memory (before answering anything personal)
```bash
python3 ~/.openclaw/workspace/skills/council-memory/scripts/memory_op.py read
```

### Write a Fact
```bash
python3 ~/.openclaw/workspace/skills/council-memory/scripts/memory_op.py write \
  --fact "Lucy decided to target bookkeepers with 5+ years experience" \
  --category "decisions"
```

### Search Memory
```bash
python3 ~/.openclaw/workspace/skills/council-memory/scripts/memory_op.py search \
  --query "bookkeeper validation"
```

### Daily Note Append
```bash
python3 ~/.openclaw/workspace/skills/council-memory/scripts/memory_op.py daily \
  --note "Rafael standup: OCR accuracy at 87%, needs 8% improvement"
```

### Inject Context for Agent
```bash
python3 ~/.openclaw/workspace/skills/council-memory/scripts/memory_op.py context \
  --agent "rafael"
```
Returns structured context string to prepend to agent prompts.

## When to Use Each Memory Layer

| Situation | Where to Write |
|---|---|
| Important decision made | MEMORY.md + council_memory.json |
| Daily event/progress | memory/YYYY-MM-DD.md |
| Agent-specific lesson | vault/Lessons/\<agent\>.md |
| Lucy preference discovered | MEMORY.md under "How Lucy Works" |
| Metric/KPI update | council_memory.json categories.kpis |
| Technical decision | MEMORY.md under "Technical Decisions" |

## Auto-Context Injection

When starting a new session or agent chat, call `context` op to get:
- Who Lucy is (one paragraph)
- Current DataFlow status
- Last 3 decisions made
- Active KPIs

This prevents agents from giving generic answers — they always know:
- Lucy = SaaS founder, Indonesia, UTC+8, DataFlow = AI OCR for bookkeepers
- Current sprint goals
- Budget constraints
- Council structure

## council_memory.json Schema

See `references/schema.md` for full schema. Key categories:
- `facts` — persistent truths about Lucy/DataFlow
- `decisions` — logged decisions with date + rationale  
- `kpis` — current metrics (OCR accuracy, bookkeepers found, etc.)
- `lessons` — what agents learned from past sessions
