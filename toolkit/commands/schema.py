"""Schema change (DDL) command"""
import argparse
import random
import string
from datetime import datetime

from utils.mysql_client import execute_sql


def random_column_name():
    """Generate random column name"""
    return 'col_' + ''.join(random.choices(string.ascii_lowercase, k=6))


def add_column(table='users'):
    """Add a random column to table"""
    col_name = random_column_name()
    col_types = [
        'VARCHAR(100)',
        'INT',
        'TEXT',
        'DATETIME',
        'BOOLEAN',
        'DECIMAL(10,2)'
    ]
    col_type = random.choice(col_types)

    sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type};"
    execute_sql(sql)

    print(f"Added column: {col_name} ({col_type}) to {table}")
    return col_name


def drop_column(table='users'):
    """Drop a non-essential column"""
    # Get existing columns (excluding essential ones)
    result = execute_sql(f"SHOW COLUMNS FROM {table};", raw=True)
    essential = ['id', 'name', 'email', 'created_at', 'updated_at', 'status']

    columns = []
    for line in result.split('\n'):
        if line:
            col_name = line.split('\t')[0]
            if col_name not in essential and col_name.startswith('col_'):
                columns.append(col_name)

    if not columns:
        print(f"No droppable columns found in {table}")
        print("Tip: Run 'add-column' first to create columns that can be dropped")
        return None

    col_to_drop = random.choice(columns)
    sql = f"ALTER TABLE {table} DROP COLUMN {col_to_drop};"
    execute_sql(sql)

    print(f"Dropped column: {col_to_drop} from {table}")
    return col_to_drop


def alter_column(table='users'):
    """Modify an existing column"""
    col_name = random_column_name()

    # First add a column, then modify it
    sql = f"ALTER TABLE {table} ADD COLUMN {col_name} VARCHAR(50);"
    execute_sql(sql)

    sql = f"ALTER TABLE {table} MODIFY COLUMN {col_name} VARCHAR(200);"
    execute_sql(sql)

    print(f"Added and modified column: {col_name} (VARCHAR(50) -> VARCHAR(200))")
    return col_name


def create_table():
    """Create a new test table"""
    table_name = 'test_' + ''.join(random.choices(string.ascii_lowercase, k=6))

    sql = f"""
    CREATE TABLE {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        data VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_sql(sql)

    # Insert a few records
    for i in range(3):
        execute_sql(f"INSERT INTO {table_name} (data) VALUES ('test data {i}');")

    print(f"Created table: {table_name} with 3 records")
    return table_name


def drop_table():
    """Drop a test table"""
    # Find droppable tables
    result = execute_sql("SHOW TABLES;", raw=True)
    protected = ['users', '_toolkit_meta']

    tables = []
    for line in result.split('\n'):
        if line and line.startswith('test_'):
            tables.append(line)

    if not tables:
        print("No droppable test tables found")
        print("Tip: Run 'create-table' first")
        return None

    table_to_drop = random.choice(tables)
    execute_sql(f"DROP TABLE {table_to_drop};")

    print(f"Dropped table: {table_to_drop}")
    return table_to_drop


def run(args):
    """Run schema change"""
    parser = argparse.ArgumentParser(description='Generate schema changes (DDL)')
    parser.add_argument('--type', required=True,
                        choices=['add-column', 'drop-column', 'alter-column',
                                 'create-table', 'drop-table'],
                        help='Type of schema change')
    parser.add_argument('--table', default='users', help='Target table')
    parser.add_argument('--count', type=int, default=1, help='Number of changes')
    opts = parser.parse_args(args)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Generating {opts.count} schema change(s): {opts.type}")
    print("-" * 40)

    for i in range(opts.count):
        if opts.type == 'add-column':
            add_column(opts.table)
        elif opts.type == 'drop-column':
            drop_column(opts.table)
        elif opts.type == 'alter-column':
            alter_column(opts.table)
        elif opts.type == 'create-table':
            create_table()
        elif opts.type == 'drop-table':
            drop_table()

    print("-" * 40)
    print("Schema change(s) complete. Check binlog for DDL events.")
