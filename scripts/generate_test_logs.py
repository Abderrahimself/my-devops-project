# #!/usr/bin/env python3
# import json
# import random
# import time
# import uuid
# import argparse
# from datetime import datetime, timedelta

# def generate_log_record(timestamp=None):
#     """Generate a single log record"""
#     # Define possible values
#     levels = ["INFO", "WARNING", "ERROR"]
#     modules = ["app", "api", "auth", "db", "task"]
#     functions = ["get_tasks", "create_task", "update_task", "delete_task", "health_check"]
#     message_templates = [
#         "Request received for {function}",
#         "Processing {function}",
#         "Completed {function} successfully",
#         "Failed to complete {function}",
#         "Database query for {function} took {time}ms",
#         "User authentication for {function}",
#         "Rate limit exceeded for {function}",
#         "Cache miss for {function}",
#         "Validation error in {function}: {error}",
#         "Test log entry: This is a sample log message for testing"
#     ]
    
#     # Create random values
#     level = random.choices(levels, weights=[0.7, 0.2, 0.1])[0]
#     module = random.choice(modules)
#     function = random.choice(functions)
    
#     # Generate a message
#     message_template = random.choice(message_templates)
#     message = message_template.format(
#         function=function,
#         time=random.randint(1, 500),
#         error=random.choice(["Invalid input", "Missing field", "Type error", "Format error"])
#     )
    
#     # Generate a timestamp if not provided
#     if timestamp is None:
#         # Random timestamp in the last 24 hours
#         now = datetime.now()
#         seconds_ago = random.randint(0, 86400)  # 24 hours in seconds
#         timestamp = (now - timedelta(seconds=seconds_ago)).isoformat()
    
#     # Generate a record
#     record = {
#         "timestamp": timestamp,
#         "level": level,
#         "message": message,
#         "module": module,
#         "function": function,
#         "line": random.randint(10, 500),
#         "request_id": str(uuid.uuid4()),
#         "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "ip": f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
#     }
    
#     return record

# def main():
#     parser = argparse.ArgumentParser(description='Generate test log records')
#     parser.add_argument('--count', type=int, default=10000, help='Number of log records to generate')
#     parser.add_argument('--output', default='test_logs.json', help='Output file name')
#     args = parser.parse_args()
    
#     print(f"Generating {args.count} log records...")
    
#     # Generate log records
#     records = []
#     for _ in range(args.count):
#         record = generate_log_record()
#         records.append(record)
    
#     # Write to file
#     with open(args.output, 'w') as f:
#         for record in records:
#             f.write(json.dumps(record) + '\n')
    
#     print(f"Generated {args.count} log records and saved to {args.output}")

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
Generate test logs for database comparison
"""
import json
import random
import argparse
import os
from datetime import datetime, timedelta

def parse_args():
    parser = argparse.ArgumentParser(description='Generate test logs')
    parser.add_argument('--count', type=int, default=1000, help='Number of logs to generate')
    parser.add_argument('--output', default='logs/test_logs.json', help='Output file for logs')
    return parser.parse_args()

def ensure_output_dir(output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

def generate_random_logs(count):
    """Generate random log entries"""
    logs = []
    
    # Define possible values
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    sources = ["app", "api", "database", "auth", "background", "scheduler"]
    message_templates = [
        "User {} logged in",
        "Request {} completed in {}ms",
        "Database query took {}ms",
        "API request to {} failed with status {}",
        "Cache hit ratio: {}%",
        "Memory usage: {}MB",
        "CPU load: {}%",
        "Failed to connect to {}",
        "Successfully processed {} items",
        "Task {} completed with status: {}"
    ]
    
    # Generate random datetime in the past week
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    time_diff_seconds = (end_time - start_time).total_seconds()
    
    for i in range(count):
        # Generate random timestamp
        random_seconds = random.randint(0, int(time_diff_seconds))
        timestamp = start_time + timedelta(seconds=random_seconds)
        
        # Generate random level (weighted)
        level_weights = [0.7, 0.15, 0.1, 0.05]  # INFO, WARNING, ERROR, DEBUG
        level = random.choices(levels, weights=level_weights, k=1)[0]
        
        # Generate random source
        source = random.choice(sources)
        
        # Generate random message
        message_template = random.choice(message_templates)
        
        # Fill in message template with random values
        if "{}" in message_template:
            if "logged in" in message_template:
                message = message_template.format(f"user_{random.randint(1, 1000)}")
            elif "Request" in message_template:
                message = message_template.format(
                    f"req_{random.randint(1000, 9999)}",
                    random.randint(10, 500)
                )
            elif "Database query" in message_template:
                message = message_template.format(random.randint(5, 200))
            elif "API request" in message_template:
                message = message_template.format(
                    f"api.example.com/v1/{random.choice(['users', 'products', 'orders'])}", 
                    random.choice([400, 401, 403, 404, 500, 502, 503])
                )
            elif "Cache hit" in message_template:
                message = message_template.format(random.randint(50, 99))
            elif "Memory usage" in message_template:
                message = message_template.format(random.randint(100, 1000))
            elif "CPU load" in message_template:
                message = message_template.format(random.randint(10, 95))
            elif "Failed to connect" in message_template:
                message = message_template.format(
                    random.choice(["database", "cache", "api.example.com", "auth-service", "queue"])
                )
            elif "Successfully processed" in message_template:
                message = message_template.format(random.randint(1, 1000))
            elif "Task" in message_template:
                message = message_template.format(
                    f"task_{random.randint(1, 1000)}", 
                    random.choice(["success", "partial", "failed", "timeout"])
                )
            else:
                message = message_template
        else:
            message = message_template
        
        # Generate random tags
        tags = {}
        
        # Add tags based on the log type
        if "logged in" in message:
            tags["user_id"] = int(message.split("user_")[1])
            tags["auth_method"] = random.choice(["password", "sso", "oauth", "totp"])
            
        elif "Request" in message:
            request_id = message.split("req_")[1].split(" ")[0]
            tags["request_id"] = request_id
            tags["method"] = random.choice(["GET", "POST", "PUT", "DELETE"])
            tags["path"] = f"/{random.choice(['api', 'web', 'admin'])}/{random.choice(['users', 'products', 'orders'])}"
            
        elif "Database query" in message:
            tags["query_type"] = random.choice(["SELECT", "INSERT", "UPDATE", "DELETE"])
            tags["table"] = random.choice(["users", "products", "orders", "logs", "settings"])
            
        elif "API request" in message:
            tags["status_code"] = int(message.split("status ")[1])
            tags["endpoint"] = message.split("to ")[1].split(" failed")[0]
            
        elif level == "ERROR":
            tags["error_code"] = f"E{random.randint(1000, 9999)}"
            tags["severity"] = random.choice(["low", "medium", "high", "critical"])
            
        # Add common tags
        tags["env"] = random.choice(["dev", "staging", "production"])
        tags["version"] = f"1.{random.randint(0, 9)}.{random.randint(0, 9)}"
        
        # Create log entry
        log = {
            "timestamp": timestamp.isoformat(),
            "level": level,
            "message": message,
            "source": source,
            "tags": tags
        }
        
        logs.append(log)
    
    return logs

def main():
    args = parse_args()
    ensure_output_dir(args.output)
    
    print(f"Generating {args.count} random log entries...")
    logs = generate_random_logs(args.count)
    
    with open(args.output, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"Generated {len(logs)} logs and saved to {args.output}")

if __name__ == "__main__":
    main()