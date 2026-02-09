"""Replication simulation command"""
import argparse
import time
import random
from datetime import datetime

from utils.mysql_client import execute_sql, get_binlog_status, flush_binary_logs


def simulate_lag(duration=60, min_delay=1, max_delay=5):
    """Simulate replica lag by inserting with delays"""
    print(f"Simulating replica lag for {duration} seconds...")
    print(f"Delay range: {min_delay}-{max_delay} seconds between operations")
    print("-" * 40)

    start_time = time.time()
    operation = 1

    while (time.time() - start_time) < duration:
        delay = random.uniform(min_delay, max_delay)
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Perform a simple operation
        execute_sql(f"UPDATE _toolkit_meta SET value='{timestamp}' WHERE key_name='version';")
        print(f"[{timestamp}] Operation #{operation} - next in {delay:.1f}s")

        operation += 1
        time.sleep(delay)

    print("-" * 40)
    print(f"Completed {operation-1} operations with simulated lag")


def simulate_disconnect():
    """Simulate connection disconnect by creating gaps"""
    print("Simulating connection disconnect...")
    print("-" * 40)

    # Record starting position
    before = get_binlog_status()
    print(f"Before: {before['file']} @ {before['position']}")

    # Flush to new binlog (simulates gap)
    flush_binary_logs()

    # Perform some operations
    for i in range(5):
        execute_sql(f"INSERT INTO users (name, email) VALUES ('Disconnect Test {i}', 'test{i}@disconnect.com');")

    # Flush again
    flush_binary_logs()

    after = get_binlog_status()
    print(f"After: {after['file']} @ {after['position']}")
    print("-" * 40)
    print("Created binlog gap - replica would need to handle file transition")


def simulate_gtid_gap():
    """Create gaps in GTID sequence"""
    print("Simulating GTID gap...")
    print("-" * 40)

    before = get_binlog_status()
    print(f"GTID before: {before['gtid']}")

    # Reset GTID (this would cause issues for replicas)
    # Note: This is a simulation - actual GTID manipulation requires SUPER privilege
    try:
        # Insert some records
        for i in range(3):
            execute_sql(f"INSERT INTO users (name, email) VALUES ('GTID Test {i}', 'gtid{i}@test.com');")

        # Flush binary logs to create new file
        flush_binary_logs()

        after = get_binlog_status()
        print(f"GTID after: {after['gtid']}")
        print("-" * 40)
        print("GTID sequence advanced - check for gaps in replica")

    except Exception as e:
        print(f"Error: {e}")
        print("Note: Some GTID operations require elevated privileges")


def run(args):
    """Run replication simulation"""
    parser = argparse.ArgumentParser(description='Simulate replication scenarios')
    parser.add_argument('--scenario', required=True,
                        choices=['lag', 'disconnect', 'gtid-gap'],
                        help='Scenario to simulate')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration in seconds (for lag scenario)')
    opts = parser.parse_args(args)

    print("=" * 50)
    print(f"Replication Scenario: {opts.scenario}")
    print("=" * 50)

    if opts.scenario == 'lag':
        simulate_lag(opts.duration)
    elif opts.scenario == 'disconnect':
        simulate_disconnect()
    elif opts.scenario == 'gtid-gap':
        simulate_gtid_gap()
