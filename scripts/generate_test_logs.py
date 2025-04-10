#!/usr/bin/env python3
import json
import random
import time
import uuid
import argparse
from datetime import datetime, timedelta

def generate_log_record(timestamp=None):
    """Generate a single log record"""
    # Define possible values
    levels = ["INFO", "WARNING", "ERROR"]
    modules = ["app", "api", "auth", "db", "task"]
    functions = ["get_tasks", "create_task", "update_task", "delete_task", "health_check"]
    message_templates = [
        "Request received for {function}",
        "Processing {function}",
        "Completed {function} successfully",
        "Failed to complete {function}",
        "Database query for {function} took {time}ms",
        "User authentication for {function}",
        "Rate limit exceeded for {function}",
        "Cache miss for {function}",
        "Validation error in {function}: {error}",
        "Test log entry: This is a sample log message for testing"
    ]
    
    # Create random values
    level = random.choices(levels, weights=[0.7, 0.2, 0.1])[0]
    module = random.choice(modules)
    function = random.choice(functions)
    
    # Generate a message
    message_template = random.choice(message_templates)
    message = message_template.format(
        function=function,
        time=random.randint(1, 500),
        error=random.choice(["Invalid input", "Missing field", "Type error", "Format error"])
    )
    
    # Generate a timestamp if not provided
    if timestamp is None:
        # Random timestamp in the last 24 hours
        now = datetime.now()
        seconds_ago = random.randint(0, 86400)  # 24 hours in seconds
        timestamp = (now - timedelta(seconds=seconds_ago)).isoformat()
    
    # Generate a record
    record = {
        "timestamp": timestamp,
        "level": level,
        "message": message,
        "module": module,
        "function": function,
        "line": random.randint(10, 500),
        "request_id": str(uuid.uuid4()),
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "ip": f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
    }
    
    return record

def main():
    parser = argparse.ArgumentParser(description='Generate test log records')
    parser.add_argument('--count', type=int, default=10000, help='Number of log records to generate')
    parser.add_argument('--output', default='test_logs.json', help='Output file name')
    args = parser.parse_args()
    
    print(f"Generating {args.count} log records...")
    
    # Generate log records
    records = []
    for _ in range(args.count):
        record = generate_log_record()
        records.append(record)
    
    # Write to file
    with open(args.output, 'w') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')
    
    print(f"Generated {args.count} log records and saved to {args.output}")

if __name__ == "__main__":
    main()