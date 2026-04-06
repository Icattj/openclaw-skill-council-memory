# council_memory.json Schema Reference

## Top-Level Structure

```json
{
  "facts": [...],       // Persistent truths about Lucy/DataFlow/Council
  "decisions": [...],   // Logged decisions with date + rationale
  "kpis": {...},        // Current KPI key-value pairs
  "lessons": [...]      // Lessons learned by agents
}
```

## facts[] entry
```json
{
  "text": "Lucy is building DataFlow, an AI OCR + accounting SaaS for Indonesian bookkeepers",
  "date": "2026-03-14",
  "category": "facts"
}
```

## decisions[] entry
```json
{
  "text": "Use direct Bedrock API instead of OpenClaw CLI (CLI hangs indefinitely)",
  "date": "2026-03-08",
  "category": "decisions"
}
```

## kpis{} — flat key:value
```json
{
  "ocr_accuracy": "87%",
  "bookkeepers_found": "0/20",
  "mrr": "$0",
  "days_to_launch": "22",
  "vps_credit_remaining": "$152"
}
```

## lessons[] entry
```json
{
  "text": "DOM createElement prevents escaping bugs vs string concatenation",
  "date": "2026-03-10",
  "category": "lesson",
  "agent": "uriel"
}
```

## Pre-seeded Facts (always inject these)

- Lucy = SaaS founder, Indonesia, UTC+8, DataFlow = AI OCR for bookkeepers
- VPS = DigitalOcean Singapore 8GB/4vCPU, $48/month after $200 credit
- 12 agents deployed: michael, rafael, uriel, gabriel, raguel, samael, sarael, azrael, remiel, zadkiel, metis, lucy_d
- Model: Claude Sonnet 4.6 via AWS Bedrock us-west-2
- Budget constraint: ~$10/month after credits expire
- DataFlow target: 500K+ Indonesian SMEs, Year 1 goal $250K revenue
