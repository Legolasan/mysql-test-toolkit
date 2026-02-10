# TC-006: Latency Degradation

## Metadata
| Field | Value |
|-------|-------|
| ID | TC-006 |
| Category | Network |
| ETL Tools | Hevo/Fivetran/Airbyte |
| Severity | Medium |
| Created | 2026-02-10 |
| Author | [Tester Name] |

## Description
Verify ETL pipeline behavior under high network latency conditions. This simulates slow network connections, cross-region replication, or degraded network performance.

## Preconditions
- [ ] MySQL toolkit running with `--cap-add=NET_ADMIN`
- [ ] ETL pipeline connected and syncing
- [ ] Initial sync completed
- [ ] Network status is clear: `toolkit network --status`

## Test Steps
1. Note current replication lag/throughput
2. Add network latency: `toolkit network --slow --latency 2000`
3. Generate data: `toolkit generate-data --count 500`
4. Observe:
   - Replication throughput reduction
   - Any timeout errors
   - Pipeline stability
5. Increase latency: `toolkit network --slow --latency 5000`
6. Observe behavior at higher latency
7. Remove latency: `toolkit network --slow --off`
8. Verify recovery

## Toolkit Commands
```bash
# Check network status
toolkit network --status

# Add 2 second latency
toolkit network --slow --latency 2000

# Add 5 second latency
toolkit network --slow --latency 5000

# Add 10 second latency (extreme)
toolkit network --slow --latency 10000

# Remove latency
toolkit network --slow --off
```

## Expected Result
- Pipeline continues to function under latency
- Replication throughput decreases proportionally
- No false-positive disconnection errors
- After latency removed:
  - Throughput returns to normal
  - No data loss

## Verification Checklist
- [ ] Pipeline remains connected under 2s latency
- [ ] Pipeline behavior under 5s latency documented
- [ ] Throughput measurements recorded
- [ ] No data loss after latency removed
- [ ] Latency successfully removed

## Cleanup
```bash
# Remove latency
toolkit network --slow --off

# Verify status
toolkit network --status
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

**Latency Test Results:**

| Latency | Throughput | Errors | Notes |
|---------|------------|--------|-------|
| 0ms (baseline) | [X rows/min] | None | Normal |
| 2000ms | [X rows/min] | [Any?] | [Notes] |
| 5000ms | [X rows/min] | [Any?] | [Notes] |

**Observations:**
- [Document behavior at each latency level]

**Screenshots/Logs:**
- [Links to artifacts]

**Notes:**
[Additional notes]
