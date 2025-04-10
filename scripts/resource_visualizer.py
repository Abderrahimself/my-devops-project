#!/usr/bin/env python3
"""
Resource metrics visualization script for database comparison
"""
import json
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

def parse_args():
    parser = argparse.ArgumentParser(description='Generate resource usage visualizations')
    parser.add_argument('--metrics', default='resource_metrics.json', help='Resource metrics JSON file')
    parser.add_argument('--output', default='reports', help='Output directory for visualizations')
    return parser.parse_args()

def ensure_output_dir(output_dir):
    """Ensure output directory exists"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def load_metrics(metrics_file):
    """Load resource metrics from JSON file"""
    if not os.path.exists(metrics_file):
        print(f"Error: Metrics file {metrics_file} not found")
        return []
        
    with open(metrics_file, 'r') as f:
        return json.load(f)

def visualize_insertion_times(metrics, output_dir):
    """Create visualization for log insertion times"""
    # Extract import operations only
    import_metrics = [m for m in metrics if m['operation'] == 'import']
    
    if not import_metrics:
        print("No import metrics found")
        return
    
    # Group by database type
    db_types = set(m['db_type'] for m in import_metrics)
    insertion_times = {db_type: [] for db_type in db_types}
    
    for metric in import_metrics:
        insertion_times[metric['db_type']].append(metric['duration_seconds'])
    
    # Calculate averages if multiple runs exist
    avg_times = {db: sum(times) / len(times) if times else 0 for db, times in insertion_times.items()}
    
    # Create bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(avg_times.keys(), avg_times.values(), color=['#3498db', '#e74c3c', '#2ecc71'])
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{height:.2f}s',
                 ha='center', va='bottom', fontweight='bold')
    
    plt.title('Log Insertion Time by Database', fontsize=16)
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.xlabel('Database', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save figure
    output_file = os.path.join(output_dir, 'insertion_time.png')
    plt.savefig(output_file, dpi=100)
    print(f"Saved insertion time chart to {output_file}")
    plt.close()

def visualize_resource_usage(metrics, output_dir):
    """Create visualizations for CPU, memory and storage usage"""
    # Extract import operations only
    import_metrics = [m for m in metrics if m['operation'] == 'import']
    
    if not import_metrics:
        print("No import metrics found")
        return
    
    # Group by database type
    db_types = set(m['db_type'] for m in import_metrics)
    
    # Prepare data structures for metrics
    cpu_usage = {db_type: [] for db_type in db_types}
    memory_usage = {db_type: [] for db_type in db_types}
    storage_change = {db_type: [] for db_type in db_types}
    
    for metric in import_metrics:
        db_type = metric['db_type']
        # Calculate average CPU during operation
        cpu_usage[db_type].append(metric['after']['cpu_percent'])
        
        # Memory in MB
        memory_change = metric['after']['memory_mb'] - metric['before']['memory_mb']
        memory_usage[db_type].append(memory_change)
        
        # Storage change in GB
        disk_change = metric['after']['disk_used_gb'] - metric['before']['disk_used_gb']
        storage_change[db_type].append(disk_change)
    
    # Calculate averages if multiple runs exist
    avg_cpu = {db: sum(usage) / len(usage) if usage else 0 for db, usage in cpu_usage.items()}
    avg_memory = {db: sum(usage) / len(usage) if usage else 0 for db, usage in memory_usage.items()}
    avg_storage = {db: sum(usage) / len(usage) if usage else 0 for db, usage in storage_change.items()}
    
    # Create CPU usage chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(avg_cpu.keys(), avg_cpu.values(), color=['#3498db', '#e74c3c', '#2ecc71'])
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{height:.1f}%',
                 ha='center', va='bottom', fontweight='bold')
    
    plt.title('CPU Usage During Log Insertion', fontsize=16)
    plt.ylabel('CPU Usage (%)', fontsize=12)
    plt.xlabel('Database', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'cpu_usage.png')
    plt.savefig(output_file, dpi=100)
    print(f"Saved CPU usage chart to {output_file}")
    plt.close()
    
    # Create memory usage chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(avg_memory.keys(), avg_memory.values(), color=['#3498db', '#e74c3c', '#2ecc71'])
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{height:.2f} MB',
                 ha='center', va='bottom', fontweight='bold')
    
    plt.title('Memory Consumption During Log Insertion', fontsize=16)
    plt.ylabel('Memory Usage Change (MB)', fontsize=12)
    plt.xlabel('Database', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'memory_usage.png')
    plt.savefig(output_file, dpi=100)
    print(f"Saved memory usage chart to {output_file}")
    plt.close()
    
    # Create storage usage chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(avg_storage.keys(), avg_storage.values(), color=['#3498db', '#e74c3c', '#2ecc71'])
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.001, f'{height:.4f} GB',
                 ha='center', va='bottom', fontweight='bold')
    
    plt.title('Storage Consumption During Log Insertion', fontsize=16)
    plt.ylabel('Storage Usage Change (GB)', fontsize=12)
    plt.xlabel('Database', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'storage_usage.png')
    plt.savefig(output_file, dpi=100)
    print(f"Saved storage usage chart to {output_file}")
    plt.close()

def create_resource_summary(metrics, output_dir):
    """Create an HTML summary of resource metrics"""
    # Extract import operations only
    import_metrics = [m for m in metrics if m['operation'] == 'import']
    
    if not import_metrics:
        print("No import metrics found")
        return
    
    # Group by database type
    db_types = list(set(m['db_type'] for m in import_metrics))
    
    # Create rows for each database
    rows = ""
    for db_type in db_types:
        db_metrics = [m for m in import_metrics if m['db_type'] == db_type]
        avg_time = sum(m['duration_seconds'] for m in db_metrics) / len(db_metrics)
        avg_cpu = sum(m['after']['cpu_percent'] for m in db_metrics) / len(db_metrics)
        avg_memory = sum(m['after']['memory_mb'] - m['before']['memory_mb'] for m in db_metrics) / len(db_metrics)
        avg_storage = sum(m['after']['disk_used_gb'] - m['before']['disk_used_gb'] for m in db_metrics) / len(db_metrics)
        
        rows += f"""
        <tr>
            <td>{db_type.capitalize()}</td>
            <td>{avg_time:.2f} sec</td>
            <td>{avg_cpu:.1f}%</td>
            <td>{avg_memory:.2f} MB</td>
            <td>{avg_storage:.4f} GB</td>
        </tr>
        """
    
    # Create HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Database Resource Usage Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; color: #333; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f1f1f1; }}
        .image-container {{ display: flex; flex-wrap: wrap; justify-content: space-around; margin: 20px 0; }}
        .image-container img {{ max-width: 45%; margin: 10px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>Database Resource Usage Summary</h1>
    
    <table>
        <tr>
            <th>Database</th>
            <th>Insertion Time</th>
            <th>CPU Usage</th>
            <th>Memory Usage</th>
            <th>Storage Usage</th>
        </tr>
        {rows}
    </table>
    
    <h2>Visualizations</h2>
    
    <div class="image-container">
        <img src="insertion_time.png" alt="Log Insertion Time" />
        <img src="cpu_usage.png" alt="CPU Usage" />
        <img src="memory_usage.png" alt="Memory Usage" />
        <img src="storage_usage.png" alt="Storage Usage" />
    </div>
</body>
</html>
"""
    
    # Write to file
    output_file = os.path.join(output_dir, 'resource_usage_report.html')
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Created resource usage summary at {output_file}")

def main():
    args = parse_args()
    ensure_output_dir(args.output)
    
    metrics = load_metrics(args.metrics)
    if not metrics:
        print("No metrics found. Exiting.")
        return
    
    visualize_insertion_times(metrics, args.output)
    visualize_resource_usage(metrics, args.output)
    create_resource_summary(metrics, args.output)
    
    print("Resource visualizations completed successfully")

if __name__ == "__main__":
    main()