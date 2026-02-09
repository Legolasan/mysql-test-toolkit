"""Data generation command"""
import random
import time
import argparse
from datetime import datetime

from utils.mysql_client import execute_sql, get_record_count

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph",
    "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa",
    "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Steven", "Ashley", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]

DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com", "company.org"]
STATUSES = ["active", "inactive", "pending"]


def generate_record():
    """Generate a single random record"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}.{random.randint(1000, 9999)}@{random.choice(DOMAINS)}"
    status = random.choice(STATUSES)
    return name, email, status


def insert_batch(count, table='users'):
    """Insert a batch of records"""
    values = []
    for _ in range(count):
        name, email, status = generate_record()
        values.append(f"('{name}', '{email}', '{status}')")

    sql = f"INSERT INTO {table} (name, email, status) VALUES {','.join(values)};"
    execute_sql(sql)


def run(args):
    """Run data generation"""
    parser = argparse.ArgumentParser(description='Generate test data')
    parser.add_argument('--count', type=int, default=100, help='Records per batch')
    parser.add_argument('--interval', type=int, default=0, help='Seconds between batches (0=one-shot)')
    parser.add_argument('--table', default='users', help='Target table')
    opts = parser.parse_args(args)

    batch = 1
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Inserting batch #{batch} ({opts.count} records)...")

            insert_batch(opts.count, opts.table)

            total = get_record_count(opts.table)
            print(f"[{timestamp}] Batch #{batch} complete. Total records: {total}")

            if opts.interval == 0:
                break

            batch += 1
            time.sleep(opts.interval)

    except KeyboardInterrupt:
        print("\nData generation stopped.")
