# TC-007: Flapping Connection

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-007 |
| Category | Network |
| ETL Tools | Hevo/Fivetran/Airbyte |
| Severity | High |
| Created | 2026-02-10 |
| Author | [Tester Name] |

## Description
Verify ETL pipeline behavior under intermittent connectivity (flapping). This simulates unstable network conditions where connections repeatedly fail and recover.

## Preconditions
- [ ] MySQL toolkit running with `--cap-add=NET_ADMIN`
- [ ] ETL pipeline connected and syncing
- [ ] Initial sync completed
- [ ] Network status is clear: `toolkit network --status`

## Test Steps
1. Start continuous data generation: `toolkit generate-data --count 50 --interval 30`
2. Enable flapping mode: `toolkit network --flap --interval 30 --duration 300`
3. Observe for 5 minutes:
   - How does pipeline handle repeated disconnects?
   - Does it recover each time?
   - Any data loss or duplication?
4. After flapping ends, verify:
   - Final pipeline state
   - Data integrity
   - Binlog position

## Toolkit Commands
```bash
# Start data generation in background
toolkit generate-data --count 50 --interval 30 &

# Flap connection every 30 seconds for 5 minutes
toolkit network --flap --type reject --interval 30 --duration 300

# Alternative: Flap with timeout (silent drop)
toolkit network --flap --type timeout --interval 30 --duration 300

# Check status after test
toolkit network --status
toolkit status
```

## Expected Result
- Pipeline handles repeated connect/disconnect cycles
- Reconnects successfully after each outage
- No data loss over the full test duration
- No duplicate records created
- Pipeline stable after flapping ends

## Verification Checklist
- [ ] Pipeline survived flapping period
- [ ] Reconnection successful each cycle
- [ ] Final row count matches expected
- [ ] No duplicate records
- [ ] Binlog position correct

## Cleanup
```bash
# Ensure network is up
toolkit network --up

# Stop any background data generation
pkill -f "generate-data"

# Verify status
toolkit network --status
toolkit status
```

---

## Test Execution Log

### Run 1 - YYYY-MM-DD
| Field | Value |
|-------|-------|
| Tester | [Name] |
| ETL Tool | [Tool] |
| Toolkit Version | 1.0.0 |
| Result | [PASS/FAIL] |

**Flapping Configuration:**
- Interval: 30 seconds
- Duration: 300 seconds (5 minutes)
- Type: reject

**Observations:**

| Cycle | Down Time | Recovery Time | Notes |
|-------|-----------|---------------|-------|
| 1 | [timestamp] | [timestamp] | [notes] |
| 2 | [timestamp] | [timestamp] | [notes] |
| ... | ... | ... | ... |

**Data Integrity:**
- Expected records: [X]
- Actual records: [X]
- Duplicates found: [Y/N]

**Screenshots/Logs:**
- [Links to artifacts]

**Notes:**
[Additional notes]
