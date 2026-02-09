#!/usr/bin/env python3
"""
MySQL Testing Toolkit - CLI Entry Point

Usage:
    toolkit <command> [options]

Commands:
    status          Show system status
    generate-data   Generate test data
    monitor         Monitor binlog position
    corrupt         Corrupt binlog for testing
    replicate       Simulate replication scenarios
    schema-change   Generate DDL events
    restore         Restore binlog from backup
    help            Show this help message
"""
import sys
import os

# Add toolkit directory to path for imports
TOOLKIT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLKIT_DIR)

from commands import generate, monitor, corrupt, replicate, schema, restore, status


COMMANDS = {
    'status': status.run,
    'generate-data': generate.run,
    'monitor': monitor.run,
    'corrupt': corrupt.run,
    'replicate': replicate.run,
    'schema-change': schema.run,
    'restore': restore.run,
}


def print_help():
    """Print help message"""
    print("""
MySQL Testing Toolkit v1.0.0
============================

Usage: toolkit <command> [options]

Commands:
  status            Show MySQL and binlog status
  generate-data     Generate test data
                    --count N       Records per batch (default: 100)
                    --interval N    Seconds between batches (0=one-shot)

  monitor           Monitor binlog position
                    --watch         Continuous monitoring
                    --json          Output as JSON

  corrupt           Corrupt binlog for testing
                    --type TYPE     truncate|random-bytes|magic-number
                    --percentage N  Truncate percentage (default: 50)
                    --no-backup     Skip creating backup

  replicate         Simulate replication scenarios
                    --scenario S    lag|disconnect|gtid-gap
                    --duration N    Duration in seconds (for lag)

  schema-change     Generate DDL events
                    --type TYPE     add-column|drop-column|alter-column|
                                    create-table|drop-table
                    --count N       Number of changes

  restore           Restore binlog from backup
                    --list          List available backups
                    --file FILE     Specific backup to restore
                    --all           Restore all backups

  help              Show this help message

Examples:
  toolkit status
  toolkit generate-data --count 100 --interval 60
  toolkit monitor --watch
  toolkit corrupt --type truncate
  toolkit schema-change --type add-column
  toolkit restore --list
""")


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command in ('help', '--help', '-h'):
        print_help()
        sys.exit(0)

    if command not in COMMANDS:
        print(f"Unknown command: {command}")
        print("Run 'toolkit help' for available commands")
        sys.exit(1)

    try:
        COMMANDS[command](args)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
