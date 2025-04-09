#!/usr/bin/env python3
import json
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def load_results(file_path):
    """Load performance results from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading results: {str(e)}")
        return None

def create_import_performance_chart(results, output_dir):
    """Create chart for import performance"""
    if not results or 'import_performance' not in results:
        print("No import performance data found")
        return
    
    # Extract data
    databases = []
    durations = []
    records_per_second = []
    
    for item in results['import_performance']:
        if 'error' not in item:
            databases.append(item['database'])
            durations.append(item['duration_seconds'])
            records_per_second.append(item['records_per_second'])
    
    # Create duration chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(databases, durations)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.2f}s',
                 ha='center', va='bottom')
    
    plt.title('Import Duration by Database')
    plt.ylabel('Duration (seconds)')
    plt.xlabel('Database')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'import_duration.png'))
    plt.close()
    
    # Create records per second chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(databases, records_per_second)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.2f}',
                 ha='center', va='bottom')
    
    plt.title('Import Speed by Database (Records per Second)')
    plt.ylabel('Records per Second')
    plt.xlabel('Database')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'import_speed.png'))
    plt.close()

def create_query_performance_chart(results, output_dir):
    """Create chart for query performance"""
    if not results or 'query_performance' not in results:
        print("No query performance data found")
        return
    
    query_types = ["level_filter", "time_range", "complex_query"]
    databases = ["PostgreSQL", "MongoDB", "Elasticsearch"]
    
    # Organize data by query type
    query_data = {}
    for query_type in query_types:
        query_data[query_type] = {}
        for db in databases:
            matches = [r for r in results['query_performance'] 
                      if r.get('database') == db and r.get('query_type') == query_type]
            if matches:
                query_data[query_type][db] = matches[0].get('avg_duration_seconds', 0)
            else:
                query_data[query_type][db] = 0
    
    # Create a grouped bar chart
    x = np.arange(len(query_types))  # the label locations
    width = 0.25  # the width of the bars
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot bars for each database
    rects1 = ax.bar(x - width, [query_data[qt]['PostgreSQL'] for qt in query_types], 
                    width, label='PostgreSQL')
    rects2 = ax.bar(x, [query_data[qt]['MongoDB'] for qt in query_types], 
                    width, label='MongoDB')
    rects3 = ax.bar(x + width, [query_data[qt]['Elasticsearch'] for qt in query_types], 
                    width, label='Elasticsearch')
    
    # Add labels and title
    ax.set_ylabel('Time (seconds)')
    ax.set_xlabel('Query Type')
    ax.set_title('Query Performance by Database and Query Type')
    ax.set_xticks(x)
    ax.set_xticklabels(query_types)
    ax.legend()
    
    # Format y-axis to scientific notation for small values
    ax.ticklabel_format(axis='y', style='scientific', scilimits=(0,0))
    
    # Add value labels on bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.6f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90, fontsize=8)
    
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    
    fig.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(output_dir, 'query_performance.png'))
    plt.close()

def create_html_report(results, output_dir):
    """Create HTML report with the visualization results"""
    if not results:
        return
    
    # Format import performance data
    import_rows = ""
    for item in results.get('import_performance', []):
        if 'error' not in item:
            import_rows += f"""
            <tr>
                <td>{item['database']}</td>
                <td>{item['total_records']}</td>
                <td>{item['duration_seconds']:.4f}</td>
                <td>{item['records_per_second']:.2f}</td>
            </tr>
            """
    
    # Format query performance data
    query_data = {}
    for item in results.get('query_performance', []):
        db = item.get('database')
        query_type = item.get('query_type')
        if 'error' not in item and db and query_type:
            if query_type not in query_data:
                query_data[query_type] = {}
            query_data[query_type][db] = item.get('avg_duration_seconds', 0)
    
    query_rows = ""
    for query_type, data in query_data.items():
        # query_rows += f"""
        # <tr>
        #     <td>{query_type}</td>
        #     <td>{data.get('PostgreSQL', 'N/A'):.6f}</td>
        #     <td>{data.get('MongoDB', 'N/A'):.6f}</td>
        #     <td>{data.get('Elasticsearch', 'N/A'):.6f}</td>
        # </tr>
        # """

        
        query_rows += """
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
        </tr>
        """.format(query_type, pg_times.get(query_type, 'N/A'), mongo_times.get(query_type, 'N/A'), es_times.get(query_type, 'N/A'))

    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Database Performance Comparison</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }}
            h2 {{
                color: #3498db;
                margin-top: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .chart-container {{
                margin: 30px 0;
                text-align: center;
            }}
            .chart {{
                max-width: 100%;
                height: auto;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                color: #7f8c8d;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Database Performance Comparison for Log Storage</h1>
            
            <h2>Summary</h2>
            <p>
                This report compares the performance of PostgreSQL, MongoDB, and Elasticsearch
                for storing and querying log data. The test was conducted with simulated DevOps logs.
            </p>
            
            <h2>Import Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Database</th>
                        <th>Records</th>
                        <th>Duration (seconds)</th>
                        <th>Records per Second</th>
                    </tr>
                </thead>
                <tbody>
                    {import_rows}
                </tbody>
            </table>
            
            <div class="chart-container">
                <h3>Import Duration</h3>
                <img class="chart" src="import_duration.png" alt="Import Duration Chart">
            </div>
            
            <div class="chart-container">
                <h3>Import Speed (Records per Second)</h3>
                <img class="chart" src="import_speed.png" alt="Import Speed Chart">
            </div>
            
            <h2>Query Performance</h2>
            <p>
                The table below shows the average execution time (in seconds) for different types of queries:
                <ul>
                    <li><strong>level_filter</strong>: Simple queries filtering by log level</li>
                    <li><strong>time_range</strong>: Queries filtering logs by time range</li>
                    <li><strong>complex_query</strong>: Complex queries combining multiple conditions</li>
                </ul>
            </p>
            
            <table>
                <thead>
                    <tr>
                        <th>Query Type</th>
                        <th>PostgreSQL (seconds)</th>
                        <th>MongoDB (seconds)</th>
                        <th>Elasticsearch (seconds)</th>
                    </tr>
                </thead>
                <tbody>
                    {query_rows}
                </tbody>
            </table>
            
            <div class="chart-container">
                <h3>Query Performance Comparison</h3>
                <img class="chart" src="query_performance.png" alt="Query Performance Chart">
            </div>
            
            <h2>Conclusion</h2>
            <p>
                Based on the performance metrics above, you can determine which database system 
                is most suitable for your specific log management needs. Consider these factors:
            </p>
            <ul>
                <li><strong>Ingest Performance</strong>: How fast the database can store new log entries</li>
                <li><strong>Query Performance</strong>: How quickly you can retrieve and analyze log data</li>
                <li><strong>Complexity of Queries</strong>: The types of analysis you need to perform</li>
            </ul>
            
            <div class="footer">
                <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    with open(os.path.join(output_dir, 'performance_report.html'), 'w') as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description='Visualize database performance comparison results')
    parser.add_argument('--results', default='performance_results.json', help='Path to results JSON file')
    parser.add_argument('--output', default='reports', help='Output directory for visualizations')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Load results
    results = load_results(args.results)
    if not results:
        print(f"No results found in {args.results}")
        return
    
    # Create visualizations
    create_import_performance_chart(results, args.output)
    create_query_performance_chart(results, args.output)
    
    # Create HTML report
    create_html_report(results, args.output)
    
    print(f"Visualizations and report created in {args.output} directory")
    print(f"Open {os.path.join(args.output, 'performance_report.html')} to view the report")

if __name__ == "__main__":
    main()