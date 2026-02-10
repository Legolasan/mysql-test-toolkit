# TC-004: Connection Refused Handling

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-004 |
| Category | Network |
| ETL Tools | Hevo/Fivetran/Airbyte |
| Severity | High |
| Created | 2026-02-10 |
| Author | [Tester Name] |

## Description
Verify ETL pipeline behavior when connections are actively refused (TCP RST). This simulates firewall blocks or service unavailability where the connection fails immediately.

## Preconditions
- [ ] MySQL toolkit running with `--cap-add=NET_ADMIN`
- [ ] ETL pipeline connected and syncing
- [ ] Initial sync completed
- [ ] Network status is clear: `toolkit network --status`

## Test Steps
1. Verify pipeline is syncing normally
2. Block connections with REJECT: `toolkit network --down --type reject`
3. Observe ETL tool behavior:
   - How quickly is the error detected?
   - What error message is shown?
   - Does it retry? How often?
4. Restore network: `toolkit network --up`
5. Verify pipeline recovery

## Toolkit Commands
```bash
# Check current network status
toolkit network --status

# Block with connection refused (immediate failure)
toolkit network --down --type reject

# Timed outage - auto-restore after 60 seconds
toolkit network --down --type reject --duration 60

# Restore network
toolkit network --up
```

## Expected Result
- ETL tool immediately detects connection refused
- Error message indicates "Connection refused" or similar
- After network restore:
  - Pipeline reconnects (automatically or manually)
  - Replication resumes correctly
- No data loss

## Verification Checklist
- [ ] Error detected immediately (< 30 seconds)
- [ ] Error message clearly indicates connection refused
- [ ] Pipeline recovers after network restore
- [ ] Replication position is maintained
- [ ] No data gaps or duplicates

## Cleanup
```bash
# Restore network
toolkit network --up

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

**Steps Performed:**
1. [Document steps]

**Observations:**
- Time to detect error: [X seconds]
- Error message: [exact text]
- Retry behavior: [description]

**Screenshots/Logs:**
- [Links to artifacts]

**Notes:**
[Additional notes]
