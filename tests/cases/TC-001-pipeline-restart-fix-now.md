# TC-001: Pipeline Restart via Fix Now

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-001 |
| Category | Recovery |
| ETL Tools | Hevo |
| Severity | Critical |
| Created | 2026-02-10 |
| Author | Arun |

## Description
Verify that an ETL pipeline restarts correctly when the "Fix Now" option is used after a failure. This tests the ETL tool's ability to recover from transient failures and resume data synchronization.

## Preconditions
- [ ] MySQL toolkit running with binlog enabled
- [ ] ETL pipeline connected and syncing
- [ ] Initial sync completed successfully
- [ ] Data is actively being generated (`toolkit generate-data --interval 60`)

## Test Steps
1. Ensure pipeline is running and syncing data normally
2. Simulate a failure scenario using one of:
   - Network failure: `toolkit network --down --type reject`
   - Binlog corruption: `toolkit corrupt --type truncate`
   - MySQL service down: `toolkit network --down --type service`
3. Wait for ETL tool to detect the failure (check pipeline status)
4. Click "Fix Now" option in the ETL tool
5. Wait for pipeline to attempt recovery
6. Restore normal operation: `toolkit network --up` or `toolkit restore --all`
7. Verify pipeline resumes syncing

## Toolkit Commands
```bash
# Option 1: Simulate network failure (connection refused)
toolkit network --down --type reject

# Option 2: Simulate network timeout
toolkit network --down --type timeout

# Option 3: Stop MySQL service
toolkit network --down --type service

# Option 4: Corrupt binlog
toolkit corrupt --type truncate

# Restore after test
toolkit network --up
toolkit restore --all
```

## Expected Result
- Pipeline detects failure and shows error status
- "Fix Now" option is available in ETL tool
- After clicking "Fix Now":
  - Pipeline status changes to successful/running
  - All tables/objects in the pipeline restart
  - Data sync resumes without data loss
  - No duplicate records created

## Verification Checklist
- [ ] Pipeline shows "Running" or "Active" status
- [ ] All objects show "Syncing" or "Completed"
- [ ] Row counts match between source and destination
- [ ] No duplicate records in destination
- [ ] Binlog position advanced correctly

## Cleanup
```bash
# Restore all connections
toolkit network --up

# Restore any corrupted binlogs
toolkit restore --all

# Verify status
toolkit status
```

---

## Test Execution Log

### Run 1 - 2026-02-10
| Field | Value |
|-------|-------|
| Tester | Arun |
| ETL Tool | Hevo |
| Toolkit Version | 1.0.0 |
| Result | PASS |

**Steps Performed:**
1. Connected Hevo pipeline to MySQL toolkit via ngrok
2. Simulated failure scenario
3. Pipeline entered failed state
4. Clicked "Fix Now" in Hevo dashboard
5. Observed recovery process

**Observations:**
- Pipeline became successful after using "Fix Now"
- All tables/objects in the pipeline got restarted
- Sync resumed correctly

**Screenshots/Logs:**
- N/A

**Notes:**
- Recovery was successful
- All objects restarted as expected
