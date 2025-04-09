#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import numpy as np
import argparse

def visualize_performance(results_file):
    """Create visualizations of database performance metrics"""
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Extract query performance data
    query_data = results.get("query_performance", [])
    
    # Organize by database and query type
    databases = ["PostgreSQL", "MongoDB", "Elasticsearch"]
    query_types = ["level_filter", "time_range", "complex_query"]
    
    # Create data structure
    performance_data = {}
    for db in databases:
        performance_data[db] = {}
        for query_type in query_types:
            # Find the result for this combination
            result = next((r for r in query_data if r.get("database") == db and r.get("query_type") == query_type), None)
            if result and "avg_duration_seconds" in result:
                performance_data[db][query_type] = result["avg_duration_seconds"]
            else:
                performance_data[db][query_type] = 0
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Set width of bars
    bar_width = 0.25
    
    # Set position of bars on x axis
    r1 = np.arange(len(query_types))
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]
    
    # Create bars
    postgres_bars = ax.bar(r1, [performance_data["PostgreSQL"][qt] for qt in query_types], 
                           width=bar_width, label='PostgreSQL', color='#0073b7')
    mongodb_bars = ax.bar(r2, [performance_data["MongoDB"][qt] for qt in query_types], 
                          width=bar_width, label='MongoDB', color='#ff851b')
    elastic_bars = ax.bar(r3, [performance_data["Elasticsearch"][qt] for qt in query_types], 
                          width=bar_width, label='Elasticsearch', color='#00a65a')
    
    # Add labels above the bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.6f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90, fontsize=8)
    
    add_labels(postgres_bars)
    add_labels(mongodb_bars)
    add_labels(elastic_bars)
    
    # Add labels and title
    ax.set_xlabel('Query Type')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Query Performance by Database and Query Type')
    ax.set_xticks([r + bar_width for r in range(len(query_types))])
    ax.set_xticklabels(query_types)
    ax.legend()
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save plot as PNG
    plt.tight_layout()
    plt.savefig('query_performance.png', dpi=300)
    print("Visualization saved as 'query_performance.png'")
    
    # If import performance data is available, create a separate visualization
    if "import_performance" in results:
        import_data = results["import_performance"]
        
        # Extract import times
        import_times = {}
        import_rates = {}
        
        for result in import_data:
            db = result.get("database")
            if db and "duration_seconds" in result:
                import_times[db] = result["duration_seconds"]
                import_rates[db] = result.get("records_per_second", 0)
        
        # Create import time comparison
        if import_times:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            dbs = list(import_times.keys())
            times = [import_times[db] for db in dbs]
            rates = [import_rates[db] for db in dbs]
            
            # Time plot
            bars1 = ax1.bar(dbs, times, color=['#0073b7', '#ff851b', '#00a65a'])
            ax1.set_title('Import Duration by Database')
            ax1.set_ylabel('Time (seconds)')
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            # Add labels
            for bar in bars1:
                height = bar.get_height()
                ax1.annotate(f'{height:.2f}s',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
            
            # Rate plot
            bars2 = ax2.bar(dbs, rates, color=['#0073b7', '#ff851b', '#00a65a'])
            ax2.set_title('Import Rate by Database')
            ax2.set_ylabel('Records per second')
            ax2.grid(True, linestyle='--', alpha=0.7)
            
            # Add labels
            for bar in bars2:
                height = bar.get_height()
                ax2.annotate(f'{height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig('import_performance.png', dpi=300)
            print("Import visualization saved as 'import_performance.png'")
    
    plt.close('all')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize database performance metrics')
    parser.add_argument('--file', default='performance_results.json', help='Path to performance results JSON file')
    args = parser.parse_args()
    
    visualize_performance(args.file)