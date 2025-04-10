# Add these imports at the top of log_analyzer.py
import psutil
import threading
import time

# Add this class to monitor resource usage
class ResourceMonitor:
    """Monitor CPU and RAM usage during database operations"""
    
    def __init__(self, interval=0.5):
        """Initialize the resource monitor
        
        Args:
            interval: Sampling interval in seconds
        """
        self.interval = interval
        self.cpu_usage = []
        self.ram_usage = []
        self.monitoring = False
        self.monitor_thread = None
    
    def _monitor_resources(self):
        """Monitor CPU and RAM usage at regular intervals"""
        while self.monitoring:
            self.cpu_usage.append(psutil.cpu_percent(interval=None))
            self.ram_usage.append(psutil.virtual_memory().percent)
            time.sleep(self.interval)
    
    def start(self):
        """Start monitoring resources"""
        self.monitoring = True
        self.cpu_usage = []
        self.ram_usage = []
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop(self):
        """Stop monitoring resources and return the results"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        # Calculate average resource usage
        avg_cpu = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        avg_ram = sum(self.ram_usage) / len(self.ram_usage) if self.ram_usage else 0
        
        # Calculate peak resource usage
        peak_cpu = max(self.cpu_usage) if self.cpu_usage else 0
        peak_ram = max(self.ram_usage) if self.ram_usage else 0
        
        return {
            'avg_cpu_percent': avg_cpu,
            'avg_ram_percent': avg_ram,
            'peak_cpu_percent': peak_cpu,
            'peak_ram_percent': peak_ram,
            'samples': len(self.cpu_usage)
        }

# Add to performance_results dictionary
performance_results = {
    'postgresql': {'insert': [], 'query': [], 'bulk_insert': [], 'cpu': [], 'ram': []},
    'mongodb': {'insert': [], 'query': [], 'bulk_insert': [], 'cpu': [], 'ram': []},
    'elasticsearch': {'insert': [], 'query': [], 'bulk_insert': [], 'cpu': [], 'ram': []}
}

# Modify store_performance_metric function
def store_performance_metric(db_type, operation, duration_ms, resource_usage=None):
    """Store a performance metric"""
    performance_results[db_type][operation].append(duration_ms)
    
    # Store resource usage if provided
    if resource_usage:
        performance_results[db_type]['cpu'].append(resource_usage['avg_cpu_percent'])
        performance_results[db_type]['ram'].append(resource_usage['avg_ram_percent'])
    
    # Also store in Elasticsearch for later analysis
    try:
        es = Elasticsearch([f'http://{ES_HOST}:{ES_PORT}'])
        
        metrics_doc = {
            'timestamp': datetime.datetime.utcnow(),
            'database': db_type,
            'operation': operation,
            'duration_ms': duration_ms
        }
        
        # Add resource usage if available
        if resource_usage:
            metrics_doc.update({
                'cpu_percent': resource_usage['avg_cpu_percent'],
                'ram_percent': resource_usage['avg_ram_percent'],
                'peak_cpu_percent': resource_usage['peak_cpu_percent'],
                'peak_ram_percent': resource_usage['peak_ram_percent']
            })
        
        es.index(
            index='performance_metrics',
            body=metrics_doc
        )
    except Exception as e:
        logger.error(f"Failed to store performance metric in Elasticsearch: {e}")

def run_benchmarks():
    """Run benchmarks for all databases"""
    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(**PG_PARAMS)
        logger.info("Connected to PostgreSQL")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        pg_conn = None
    
    # Connect to MongoDB
    try:
        mongo_client = pymongo.MongoClient(MONGO_URI)
        mongo_db = mongo_client[MONGO_DB]
        mongo_collection = mongo_db['app_logs']
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        mongo_collection = None
    
    # Connect to Elasticsearch
    try:
        es_client = Elasticsearch([f'http://{ES_HOST}:{ES_PORT}'])
        if not es_client.indices.exists(index=ES_INDEX):
            es_client.indices.create(
                index=ES_INDEX,
                body={
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "level": {"type": "keyword"},
                            "message": {"type": "text"},
                            "source": {"type": "keyword"},
                            "details": {"type": "object", "dynamic": True}
                        }
                    }
                }
            )
        logger.info("Connected to Elasticsearch")
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        es_client = None
    
    # Run single insert benchmarks
    logger.info("Running single insert benchmarks...")
    for i in range(100):
        log_entry = generate_log_entry()
        
        # PostgreSQL
        if pg_conn:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(pg_insert_log, pg_conn, log_entry)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('postgresql', 'insert', duration, resource_usage)
        
        # MongoDB
        if mongo_collection:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(mongo_insert_log, mongo_collection, log_entry)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('mongodb', 'insert', duration, resource_usage)
        
        # Elasticsearch
        if es_client:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(es_insert_log, es_client, log_entry)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('elasticsearch', 'insert', duration, resource_usage)
    
    # Run bulk insert benchmarks
    logger.info("Running bulk insert benchmarks...")
    for i in range(10):
        logs = generate_logs(100)  # Generate 100 logs per batch
        
        # PostgreSQL
        if pg_conn:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(pg_bulk_insert_logs, pg_conn, logs)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('postgresql', 'bulk_insert', duration, resource_usage)
        
        # MongoDB
        if mongo_collection:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(mongo_bulk_insert_logs, mongo_collection, logs)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('mongodb', 'bulk_insert', duration, resource_usage)
        
        # Elasticsearch
        if es_client:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(es_bulk_insert_logs, es_client, logs)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('elasticsearch', 'bulk_insert', duration, resource_usage)
    
    # Run query benchmarks
    logger.info("Running query benchmarks...")
    for i in range(50):
        level = random.choice(LOG_LEVELS)
        
        # PostgreSQL
        if pg_conn:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(pg_query_logs, pg_conn, level)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('postgresql', 'query', duration, resource_usage)
        
        # MongoDB
        if mongo_collection:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(mongo_query_logs, mongo_collection, level)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('mongodb', 'query', duration, resource_usage)
        
        # Elasticsearch
        if es_client:
            # Create and start resource monitor
            resource_monitor = ResourceMonitor()
            resource_monitor.start()
            
            # Measure execution time
            _, duration = measure_execution_time(es_query_logs, es_client, level)
            
            # Stop monitoring and get resource usage
            resource_usage = resource_monitor.stop()
            
            # Store metrics
            store_performance_metric('elasticsearch', 'query', duration, resource_usage)
    
    # Clean up connections
    if pg_conn:
        pg_conn.close()
    
    if mongo_client:
        mongo_client.close()
    
    # No explicit close needed for Elasticsearch


def generate_performance_report():
    # ... existing code ...
    
    # Add resource usage chart
    fig_resources = plt.figure(figsize=(12, 8))
    
    # CPU usage subplot
    ax1 = fig_resources.add_subplot(2, 1, 1)
    avg_cpu = []
    for db_type in ['postgresql', 'mongodb', 'elasticsearch']:
        if db_type in avg_results and 'cpu' in avg_results[db_type]:
            avg_cpu.append(avg_results[db_type]['cpu'])
        else:
            avg_cpu.append(0)
    
    ax1.bar(['PostgreSQL', 'MongoDB', 'Elasticsearch'], avg_cpu)
    ax1.set_ylabel('Average CPU Usage (%)')
    ax1.set_title('CPU Usage by Database')
    
    # RAM usage subplot
    ax2 = fig_resources.add_subplot(2, 1, 2)
    avg_ram = []
    for db_type in ['postgresql', 'mongodb', 'elasticsearch']:
        if db_type in avg_results and 'ram' in avg_results[db_type]:
            avg_ram.append(avg_results[db_type]['ram'])
        else:
            avg_ram.append(0)
    
    ax2.bar(['PostgreSQL', 'MongoDB', 'Elasticsearch'], avg_ram)
    ax2.set_ylabel('Average RAM Usage (%)')
    ax2.set_title('RAM Usage by Database')
    
    fig_resources.tight_layout()
    plt.savefig('resource_usage_comparison.png')
    logger.info("Resource usage chart saved as resource_usage_comparison.png")
    
    # Update CSV report to include resource metrics
    with open('performance_report.csv', 'w') as f:
        f.write("Database,Operation,Average Duration (ms),Average CPU (%),Average RAM (%)\n")
        for db_type in avg_results:
            for operation in ['insert', 'bulk_insert', 'query']:
                cpu_usage = avg_results[db_type].get('cpu', 0)
                ram_usage = avg_results[db_type].get('ram', 0)
                f.write(f"{db_type},{operation},{avg_results[db_type].get(operation, 0):.2f},{cpu_usage:.2f},{ram_usage:.2f}\n")