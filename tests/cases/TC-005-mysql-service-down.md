# TC-005: MySQL Service Down

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-005 |
| Category | Network |
| ETL Tools | Hevo/Fivetran/Airbyte |
| Severity | Critical |
| Created | 2026-02-10 |
| Author | [Tester Name] |

## Description
Verify ETL pipeline behavior when MySQL service is completely stopped. This simulates database server crashes, maintenance windows, or unplanned outages.

## Preconditions
- [ ] MySQL toolkit running
- [ ] ETL pipeline connected and syncing
- [ ] Initial sync completed
- [ ] MySQL is running: `toolkit status`

## Test Steps
1. Verify MySQL is running and pipeline is syncing
2. Stop MySQL service: `toolkit network --down --type service`
3. Observe ETL tool behavior:
   - Error detection time
   - Error message content
   - Retry behavior
4. Start MySQL service: `toolkit network --up`
5. Verify pipeline recovery
6. Check data integrity

## Toolkit Commands
```bash
# Check MySQL status
toolkit status

# Stop MySQL service
toolkit network --down --type service

# Start MySQL service
toolkit network --up

# Or use --up to restore everything
toolkit network --up
```

## Expected Result
- ETL tool detects MySQL unavailability
- Error message indicates "MySQL server has gone away" or connection lost
- After MySQL restart:
  - Pipeline reconnects
  - Binlog position is maintained
  - Replication resumes without data loss

## Verification Checklist
- [ ] MySQL successfully stopped
- [ ] ETL tool detects disconnection
- [ ] MySQL successfully restarted
- [ ] Pipeline reconnects after restart
- [ ] Binlog position maintained
- [ ] No data loss or duplication

## Cleanup
```bash
# Ensure MySQL is running
toolkit network --up

# Verify status
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
- MySQL stop time: [X seconds]
- Error detection time: [X seconds]
- MySQL restart time: [X seconds]
- Recovery time: [X seconds]

**Screenshots/Logs:**
- [Links to artifacts]

**Notes:**
[Additional notes]
