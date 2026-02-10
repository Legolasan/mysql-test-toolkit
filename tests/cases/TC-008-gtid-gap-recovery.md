# TC-008: GTID Gap Recovery

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-008 |
| Category | Replication |
| ETL Tools | Hevo/Fivetran/Airbyte |
| Severity | Critical |
| Created | 2026-02-10 |
| Author | [Tester Name] |

## Description
Verify ETL pipeline behavior when GTID gaps are introduced. This simulates scenarios where transactions are skipped or lost, creating gaps in the GTID sequence.

## Preconditions
- [ ] MySQL toolkit running with GTID enabled
- [ ] ETL pipeline connected and syncing via GTID
- [ ] Initial sync completed
- [ ] Current GTID set noted: `toolkit status`

## Test Steps
1. Note current GTID set: `toolkit status`
2. Create GTID gap: `toolkit replicate --scenario gtid-gap`
3. Generate new data: `toolkit generate-data --count 100`
4. Observe ETL tool behavior:
   - Does it detect the gap?
   - What error message is shown?
   - How does it handle the gap?
5. Attempt recovery
6. Verify data integrity

## Toolkit Commands
```bash
# Check current GTID status
toolkit status

# Create GTID gap
toolkit replicate --scenario gtid-gap

# Generate data after gap
toolkit generate-data --count 100

# Check status after
toolkit status
```

## Expected Result
- ETL tool detects GTID gap
- Clear error message indicates missing transactions
- Recovery options:
  - Re-snapshot from source
  - Manual GTID adjustment
  - Tool-specific gap handling
- After recovery, sync continues correctly

## Verification Checklist
- [ ] GTID gap successfully created
- [ ] ETL tool detected the gap
- [ ] Error message is clear and actionable
- [ ] Recovery method documented
- [ ] Data integrity verified after recovery

## Cleanup
```bash
# Note: GTID gaps may require re-snapshot
# or manual intervention to fully recover

# Check final status
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

**GTID Information:**
- Before gap: [GTID set]
- After gap: [GTID set]
- Gap size: [X transactions]

**Observations:**
- Error message: [exact text]
- Recovery method used: [description]

**Screenshots/Logs:**
- [Links to artifacts]

**Notes:**
[Additional notes about GTID gap handling]
