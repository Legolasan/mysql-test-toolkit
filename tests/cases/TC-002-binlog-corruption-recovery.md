# TC-002: Binlog Corruption Recovery

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-002 |
| Category | Binlog |
| ETL Tools | Hevo/Fivetran/Airbyte |
| Severity | Critical |
| Created | 2026-02-10 |
| Author | [Tester Name] |

## Description
Verify ETL pipeline behavior when MySQL binlog file is corrupted mid-replication. Tests the pipeline's ability to detect corruption, handle errors gracefully, and recover after binlog is restored.

## Preconditions
- [ ] MySQL toolkit running with binlog enabled
- [ ] ETL pipeline connected and actively replicating
- [ ] Initial sync completed
- [ ] Current binlog position noted: `toolkit monitor`

## Test Steps
1. Note current binlog file and position: `toolkit monitor`
2. Generate some data: `toolkit generate-data --count 100`
3. Corrupt the binlog file: `toolkit corrupt --type truncate`
4. Wait for ETL tool to encounter the corruption
5. Observe error handling behavior
6. Restore binlog: `toolkit restore --all`
7. Attempt pipeline recovery (Fix Now or manual restart)
8. Verify data integrity

## Toolkit Commands
```bash
# Check current binlog position
toolkit monitor

# Generate data to create binlog entries
toolkit generate-data --count 100

# Corrupt binlog (truncate at 50%)
toolkit corrupt --type truncate

# Alternative: Corrupt magic number (makes file unreadable)
toolkit corrupt --type magic-number

# Alternative: Inject random bytes
toolkit corrupt --type random-bytes

# List available backups
toolkit restore --list

# Restore all backups
toolkit restore --all
```

## Expected Result
- ETL tool detects binlog read error
- Clear error message indicates corruption or incomplete binlog
- After restoration:
  - Pipeline can be restarted
  - Replication resumes from valid position
  - No data loss (may require re-sync from snapshot)

## Verification Checklist
- [ ] Error message clearly indicates binlog issue
- [ ] Binlog backup was created before corruption
- [ ] Restore command successfully recovers binlog
- [ ] Pipeline can resume after restore
- [ ] Data integrity maintained

## Cleanup
```bash
# Restore corrupted binlog
toolkit restore --all

# Verify binlog is readable
toolkit monitor

# Check MySQL status
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
- [Document observations]

**Screenshots/Logs:**
- [Links to artifacts]

**Notes:**
[Additional notes]
