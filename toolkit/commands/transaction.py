"""Large transaction simulation command"""
import argparse
import random
import string
import time
from datetime import datetime

from utils.mysql_client import execute_sql, get_record_count


def generate_random_text(size_kb):
    """Generate random text of specified size in KB"""
    size_bytes = size_kb * 1024
    return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=size_bytes))


def generate_random_blob(size_kb):
    """Generate random binary data of specified size in KB"""
    size_bytes = size_kb * 1024
    return ''.join(random.choices(string.hexdigits, k=size_bytes * 2))


def ensure_large_data_table():
    """Create table for large data if not exists"""
    sql = """
    CREATE TABLE IF NOT EXISTS large_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        data_text LONGTEXT,
        data_blob LONGBLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_sql(sql)


def large_row_count_transaction(row_count, table='users'):
    """Execute a transaction with many rows"""
    print(f"Starting transaction with {row_count} rows...")
    start_time = time.time()

    # Build large INSERT with multiple VALUES
    # Split into batches of 1000 to avoid query size limits
    batch_size = 1000
    total_inserted = 0

    execute_sql("START TRANSACTION;")

    try:
        for batch_start in range(0, row_count, batch_size):
            batch_count = min(batch_size, row_count - batch_start)
            values = []

            for i in range(batch_count):
                first = random.choice(["John", "Jane", "Bob", "Alice", "Charlie"])
                last = random.choice(["Smith", "Doe", "Johnson", "Williams", "Brown"])
                name = f"{first} {last}"
                email = f"{first.lower()}.{last.lower()}.{random.randint(1000,9999)}@example.com"
                values.append(f"('{name}', '{email}', 'active')")

            sql = f"INSERT INTO {table} (name, email, status) VALUES {','.join(values)};"
            execute_sql(sql)
            total_inserted += batch_count
            print(f"  Inserted {total_inserted}/{row_count} rows...")

        execute_sql("COMMIT;")
        elapsed = time.time() - start_time
        print(f"Transaction committed: {row_count} rows in {elapsed:.2f}s")

    except Exception as e:
        execute_sql("ROLLBACK;")
        print(f"Transaction rolled back: {e}")
        raise


def large_data_size_transaction(row_count, size_kb_per_row, data_type='text'):
    """Execute a transaction with large data per row"""
    ensure_large_data_table()

    print(f"Starting transaction: {row_count} rows x {size_kb_per_row}KB {data_type} each...")
    print(f"Total data size: ~{row_count * size_kb_per_row / 1024:.1f}MB")
    start_time = time.time()

    execute_sql("START TRANSACTION;")

    try:
        for i in range(row_count):
            if data_type == 'text':
                data = generate_random_text(size_kb_per_row)
                sql = f"INSERT INTO large_data (data_text) VALUES ('{data}');"
            else:  # blob
                data = generate_random_blob(size_kb_per_row)
                sql = f"INSERT INTO large_data (data_blob) VALUES (UNHEX('{data}'));"

            execute_sql(sql)

            if (i + 1) % 10 == 0 or i == row_count - 1:
                print(f"  Inserted {i + 1}/{row_count} rows...")

        execute_sql("COMMIT;")
        elapsed = time.time() - start_time
        print(f"Transaction committed: {row_count} rows ({row_count * size_kb_per_row}KB) in {elapsed:.2f}s")

    except Exception as e:
        execute_sql("ROLLBACK;")
        print(f"Transaction rolled back: {e}")
        raise


def long_running_transaction(duration_seconds, operations_per_second=1):
    """Hold a transaction open for extended time"""
    print(f"Starting long-running transaction for {duration_seconds}s...")
    print(f"Operations: {operations_per_second}/second")
    print("This will hold locks and generate continuous binlog events")
    print("-" * 40)

    start_time = time.time()
    operation_count = 0

    execute_sql("START TRANSACTION;")

    try:
        while (time.time() - start_time) < duration_seconds:
            # Perform an update operation
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            execute_sql(f"UPDATE _toolkit_meta SET value='{timestamp}', updated_at=NOW() WHERE key_name='version';")
            operation_count += 1

            elapsed = time.time() - start_time
            remaining = duration_seconds - elapsed
            print(f"  [{elapsed:.0f}s] Operations: {operation_count}, Remaining: {remaining:.0f}s")

            time.sleep(1.0 / operations_per_second)

        execute_sql("COMMIT;")
        elapsed = time.time() - start_time
        print("-" * 40)
        print(f"Transaction committed after {elapsed:.1f}s with {operation_count} operations")

    except KeyboardInterrupt:
        execute_sql("COMMIT;")
        print("\nTransaction committed early (interrupted)")
    except Exception as e:
        execute_sql("ROLLBACK;")
        print(f"Transaction rolled back: {e}")
        raise


def mixed_large_transaction(row_count, size_kb, duration_seconds):
    """Combined large transaction: many rows + large data + held open"""
    ensure_large_data_table()

    print("=" * 50)
    print("MIXED LARGE TRANSACTION")
    print("=" * 50)
    print(f"Rows: {row_count}")
    print(f"Data size per row: {size_kb}KB")
    print(f"Minimum duration: {duration_seconds}s")
    print(f"Total data: ~{row_count * size_kb / 1024:.1f}MB")
    print("=" * 50)

    start_time = time.time()
    execute_sql("START TRANSACTION;")

    try:
        # Insert rows with large data
        for i in range(row_count):
            data = generate_random_text(size_kb)
            sql = f"INSERT INTO large_data (data_text) VALUES ('{data}');"
            execute_sql(sql)

            if (i + 1) % 10 == 0:
                print(f"  Inserted {i + 1}/{row_count} rows...")

        # Hold transaction open if needed
        elapsed = time.time() - start_time
        if elapsed < duration_seconds:
            remaining = duration_seconds - elapsed
            print(f"Holding transaction open for {remaining:.0f}s more...")
            time.sleep(remaining)

        execute_sql("COMMIT;")
        total_elapsed = time.time() - start_time
        print("=" * 50)
        print(f"Transaction committed: {row_count} rows in {total_elapsed:.1f}s")

    except KeyboardInterrupt:
        execute_sql("COMMIT;")
        print("\nTransaction committed early (interrupted)")
    except Exception as e:
        execute_sql("ROLLBACK;")
        print(f"Transaction rolled back: {e}")
        raise


def run(args):
    """Run large transaction simulation"""
    parser = argparse.ArgumentParser(description='Simulate large transactions')
    parser.add_argument('--type', required=True,
                        choices=['many-rows', 'large-data', 'long-running', 'mixed'],
                        help='Type of large transaction')
    parser.add_argument('--rows', type=int, default=1000,
                        help='Number of rows (default: 1000)')
    parser.add_argument('--size', type=int, default=100,
                        help='Data size in KB per row (default: 100)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration in seconds for long-running (default: 60)')
    parser.add_argument('--data-type', choices=['text', 'blob'], default='text',
                        help='Data type for large-data (default: text)')
    parser.add_argument('--ops-per-sec', type=int, default=1,
                        help='Operations per second for long-running (default: 1)')
    opts = parser.parse_args(args)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Large Transaction Simulation")
    print(f"Type: {opts.type}")
    print("-" * 40)

    if opts.type == 'many-rows':
        large_row_count_transaction(opts.rows)
    elif opts.type == 'large-data':
        large_data_size_transaction(opts.rows, opts.size, opts.data_type)
    elif opts.type == 'long-running':
        long_running_transaction(opts.duration, opts.ops_per_sec)
    elif opts.type == 'mixed':
        mixed_large_transaction(opts.rows, opts.size, opts.duration)

    print("-" * 40)
    print("Check binlog size: toolkit monitor")
