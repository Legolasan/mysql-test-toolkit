# TC-003: Network Timeout Handling

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-003 |
| Category | Network |
| ETL Tools | Hevo/Fivetran/Airbyte |
| Severity | High |
| Created | 2026-02-10 |
| Author | [Tester Name] |

## Description
Verify ETL pipeline behavior when network connections timeout (packets dropped silently). This simulates network issues where connections hang indefinitely rather than failing immediately.

## Preconditions
- [ ] MySQL toolkit running with `--cap-add=NET_ADMIN`
- [ ] ETL pipeline connected and syncing
- [ ] Initial sync completed
- [ ] Network status is clear: `toolkit network --status`

## Test Steps
1. Verify pipeline is syncing: check ETL dashboard
2. Enable network timeout (DROP): `toolkit network --down --type timeout`
3. Observe ETL tool behavior:
   - How long until timeout detected?
   - What error message is shown?
   - Does it retry automatically?
4. Restore network: `toolkit network --up`
5. Verify pipeline recovery

## Toolkit Commands
```bash
# Check current network status
toolkit network --status

# Enable timeout (silent packet drop)
toolkit network --down --type timeout

# Timed outage - auto-restore after 60 seconds
toolkit network --down --type timeout --duration 60

# Restore network
toolkit network --up
```

## Expected Result
- ETL tool eventually detects connection timeout
- Error message indicates timeout or connection lost
- After network restore:
  - Pipeline reconnects automatically OR
  - Manual intervention triggers successful reconnection
- No data loss or duplication

## Verification Checklist
- [ ] Timeout detected within reasonable time (< 5 minutes)
- [ ] Error message is clear and actionable
- [ ] Pipeline recovers after network restore
- [ ] Replication resumes from correct position
- [ ] No duplicate data created

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
- Time to detect timeout: [X minutes]
- Error message: [exact text]
- Recovery behavior: [automatic/manual]

**Screenshots/Logs:**
- [Links to artifacts]

**Notes:**
[Additional notes]
