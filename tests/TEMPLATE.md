# TC-XXX: [Test Title]

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-XXX |
| Category | [Network/Binlog/Replication/Schema/Transaction] |
| ETL Tools | [Hevo/Fivetran/Airbyte/Stitch/etc.] |
| Severity | [Critical/High/Medium/Low] |
| Created | YYYY-MM-DD |
| Author | [Name] |

## Description
[Brief description of what this test validates]

## Preconditions
- [ ] MySQL toolkit running (`docker ps` shows container)
- [ ] Binlog enabled and ROW format verified (`toolkit status`)
- [ ] ETL pipeline connected and initial sync completed
- [ ] Test data present in `testdb.users` table

## Test Steps
1. [First step]
2. [Second step]
3. [Third step]
4. ...

## Toolkit Commands
```bash
# Commands to simulate the scenario
toolkit [command] [options]
```

## Expected Result
- [Expected behavior 1]
- [Expected behavior 2]
- [Expected behavior 3]

## Verification Checklist
- [ ] [Verification item 1]
- [ ] [Verification item 2]
- [ ] [Verification item 3]

## Cleanup
```bash
# Commands to restore normal operation
toolkit network --up
toolkit restore --all
```

---

## Test Execution Log

### Run 1 - YYYY-MM-DD
| Field | Value |
|-------|-------|
| Tester | [Name] |
| ETL Tool | [Tool name and version] |
| Toolkit Version | [Version] |
| Result | PASS / FAIL |

**Steps Performed:**
1. [What you did]
2. [What you did]

**Observations:**
- [What you saw]
- [What you saw]

**Screenshots/Logs:**
- [Link to screenshot or log file in results/ folder]

**Notes:**
[Any additional observations or issues]

---

### Run 2 - YYYY-MM-DD
[Copy the template above for additional runs]
