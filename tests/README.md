# ETL/CDC Test Cases

Test case documentation for validating ETL pipeline resilience using the MySQL Testing Toolkit.

## Quick Start

1. **Run a test scenario:**
   ```bash
   # Start the toolkit
   docker run -d -p 3306:3306 --cap-add=NET_ADMIN --name mysql-toolkit arunsunderraj91/mysql-test-toolkit

   # Connect your ETL tool to MySQL
   # Host: localhost, Port: 3306, User: hevo, Password: hevopassword

   # Simulate a failure (e.g., network timeout)
   docker exec mysql-toolkit toolkit network --down --type timeout --duration 60
   ```

2. **Document your results:**
   - Copy `TEMPLATE.md` to `cases/TC-XXX-your-test.md`
   - Fill in the test steps and expected results
   - Log your execution results in the Test Execution Log section

## Folder Structure

```
tests/
├── README.md           # This file
├── TEMPLATE.md         # Blank template for new test cases
├── results/            # Screenshots, logs, exported data
└── cases/              # Test case documentation
    ├── TC-001-*.md
    ├── TC-002-*.md
    └── ...
```

## Test Categories

| Category | Description | Toolkit Commands |
|----------|-------------|------------------|
| **Network** | Connection failures, timeouts, latency | `toolkit network` |
| **Binlog** | Corruption, truncation, gaps | `toolkit corrupt` |
| **Replication** | GTID gaps, replica lag | `toolkit replicate` |
| **Schema** | DDL changes during sync | `toolkit schema-change` |
| **Transaction** | Large/long transactions | `toolkit transaction` |

## Available Test Cases

| ID | Title | Category | Status |
|----|-------|----------|--------|
| TC-001 | Pipeline Restart via Fix Now | Recovery | Executed |
| TC-002 | Binlog Corruption Recovery | Binlog | Template |
| TC-003 | Network Timeout Handling | Network | Template |
| TC-004 | Connection Refused Handling | Network | Template |
| TC-005 | MySQL Service Down | Network | Template |
| TC-006 | Latency Degradation | Network | Template |
| TC-007 | Flapping Connection | Network | Template |
| TC-008 | GTID Gap Recovery | Replication | Template |

## Running Tests

### Prerequisites
- Docker installed
- ETL tool account (Hevo, Fivetran, Airbyte, etc.)
- MySQL Testing Toolkit running

### Test Workflow
1. Set up initial pipeline and complete first sync
2. Choose a test case from `cases/`
3. Execute the toolkit commands to simulate the scenario
4. Observe ETL tool behavior
5. Document results in the test case file
6. Restore normal operation: `toolkit network --up`

## Contributing Test Cases

1. Copy `TEMPLATE.md` to `cases/TC-XXX-descriptive-name.md`
2. Fill in all sections
3. Run the test and document results
4. Submit a PR with your test case
