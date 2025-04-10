# #!/usr/bin/env python3
# import os
# import json
# import time
# import argparse
# import psycopg2
# from datetime import datetime
# import pymongo
# from elasticsearch import Elasticsearch
# import random

# def read_log_file(file_path):
#     """Read log records from JSON log file"""
#     records = []
#     try:
#         with open(file_path, 'r') as f:
#             for line in f:
#                 try:
#                     records.append(json.loads(line.strip()))
#                 except json.JSONDecodeError:
#                     continue
#         return records
#     except Exception as e:
#         print(f"Error reading log file: {str(e)}")
#         return []

# def import_to_postgres(records, batch_size=100):
#     """Import log records to PostgreSQL"""
#     try:
#         # conn = psycopg2.connect(
#         #     host="localhost",
#         #     database="taskdb",
#         #     user="devops",
#         #     password="devops_password"
#         # )

#         conn = psycopg2.connect(
#             host="postgres-db",  # Use the service name from docker-compose
#             database="taskdb",
#             user="devops",
#             password="devops_password"
#         )
#         cursor = conn.cursor()
        
#         start_time = time.time()
#         total_records = len(records)
#         imported = 0
        
#         for i in range(0, total_records, batch_size):
#             batch = records[i:i+batch_size]
#             for record in batch:
#                 cursor.execute(
#                     """
#                     INSERT INTO logs 
#                     (timestamp, level, message, module, function, line, request_id, user_agent, ip, raw_log)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                     """,
#                     (
#                         datetime.fromisoformat(record.get('timestamp')),
#                         record.get('level'),
#                         record.get('message'),
#                         record.get('module'),
#                         record.get('function'),
#                         record.get('line'),
#                         record.get('request_id'),
#                         record.get('user_agent'),
#                         record.get('ip'),
#                         json.dumps(record)
#                     )
#                 )
#             conn.commit()
#             imported += len(batch)
#             print(f"PostgreSQL: Imported {imported}/{total_records} records")
        
#         end_time = time.time()
#         duration = end_time - start_time
        
#         cursor.close()
#         conn.close()
        
#         return {
#             "database": "PostgreSQL",
#             "total_records": total_records,
#             "duration_seconds": duration,
#             "records_per_second": total_records / duration if duration > 0 else 0
#         }
#     except Exception as e:
#         print(f"Error importing to PostgreSQL: {str(e)}")
#         return {
#             "database": "PostgreSQL",
#             "error": str(e)
#         }

# def import_to_mongodb(records, batch_size=100):
#     """Import log records to MongoDB"""
#     try:
#         # client = pymongo.MongoClient(
#         #     "mongodb://devops:devops_password@localhost:27017/admin"
#         # )

#         client = pymongo.MongoClient(
#             "mongodb://devops:devops_password@mongodb:27017/admin"  # Use the service name
#         )
#         db = client.logs
#         collection = db.app_logs
        
#         start_time = time.time()
#         total_records = len(records)
        
#         # Insert in batches
#         for i in range(0, total_records, batch_size):
#             batch = records[i:i+batch_size]
#             collection.insert_many(batch)
#             print(f"MongoDB: Imported {min(i+batch_size, total_records)}/{total_records} records")
        
#         end_time = time.time()
#         duration = end_time - start_time
        
#         client.close()
        
#         return {
#             "database": "MongoDB",
#             "total_records": total_records,
#             "duration_seconds": duration,
#             "records_per_second": total_records / duration if duration > 0 else 0
#         }
#     except Exception as e:
#         print(f"Error importing to MongoDB: {str(e)}")
#         return {
#             "database": "MongoDB",
#             "error": str(e)
#         }

# # def import_to_elasticsearch(records, batch_size=100):
#     """Import log records to Elasticsearch"""
#     try:
#         from elasticsearch import Elasticsearch
        
#         # Connect to Elasticsearch
#         print("Connecting to Elasticsearch...")
#         # es = Elasticsearch(["http://localhost:9200"])
#         es = Elasticsearch(["http://elasticsearch:9200"])  # Use the service name        
#         # Check connection
#         if not es.ping():
#             print("Cannot connect to Elasticsearch! Please check if it's running.")
#             return {
#                 "database": "Elasticsearch",
#                 "error": "Failed to connect to Elasticsearch"
#             }
        
#         print(f"Elasticsearch connection successful")
        
#         start_time = time.time()
#         total_records = len(records)
#         imported = 0
        
#         # Bulk insert
#         for i in range(0, total_records, batch_size):
#             batch = records[i:i+batch_size]
#             bulk_data = []
            
#             for record in batch:
#                 # Clean any problematic fields for ES
#                 clean_record = record.copy()
#                 # Ensure timestamp is in proper format
#                 if 'timestamp' in clean_record:
#                     try:
#                         datetime.fromisoformat(clean_record['timestamp'])
#                     except ValueError:
#                         clean_record['timestamp'] = datetime.now().isoformat()
                
#                 # Add index action
#                 bulk_data.append({"index": {"_index": "logs"}})
#                 bulk_data.append(clean_record)
            
#             if bulk_data:
#                 try:
#                     response = es.bulk(body=bulk_data)
#                     if response.get('errors'):
#                         print(f"Some errors occurred in bulk insert")
#                 except Exception as e:
#                     print(f"Error in bulk insert: {str(e)}")
#                     # Try individual inserts
#                     for j in range(0, len(batch)):
#                         try:
#                             es.index(index="logs", body=batch[j])
#                         except Exception as inner_e:
#                             print(f"Error indexing single record: {str(inner_e)}")
            
#             imported += len(batch)
#             print(f"Elasticsearch: Imported {imported}/{total_records} records")
        
#         end_time = time.time()
#         duration = end_time - start_time
        
#         return {
#             "database": "Elasticsearch",
#             "total_records": total_records,
#             "duration_seconds": duration,
#             "records_per_second": total_records / duration if duration > 0 else 0
#         }
#     except Exception as e:
#         print(f"Error importing to Elasticsearch: {str(e)}")
#         return {
#             "database": "Elasticsearch",
#             "error": str(e)
#         }

# def import_to_elasticsearch(records, batch_size=100):
#     """Import log records to Elasticsearch"""
#     try:
#         # Connect to Elasticsearch
#         print("Connecting to Elasticsearch...")
#         es = Elasticsearch(["http://elasticsearch:9200"])  # Use the service name
        
#         # Check connection
#         if not es.ping():
#             print("Cannot connect to Elasticsearch! Please check if it's running.")
#             return {
#                 "database": "Elasticsearch",
#                 "error": "Failed to connect to Elasticsearch"
#             }
        
#         print("Elasticsearch connection successful")
        
#         # Make sure the index exists with proper mappings
#         if not es.indices.exists(index="logs"):
#             print("Creating 'logs' index with proper mappings...")
#             # Define proper mappings for log data
#             mappings = {
#                 "mappings": {
#                     "properties": {
#                         "timestamp": {"type": "date"},
#                         "level": {"type": "keyword"},
#                         "message": {"type": "text"},
#                         "module": {"type": "keyword"},
#                         "function": {"type": "keyword"},
#                         "line": {"type": "integer"},
#                         "request_id": {"type": "keyword"},
#                         "user_agent": {"type": "text"},
#                         "ip": {"type": "ip"}
#                     }
#                 }
#             }
#             es.indices.create(index="logs", body=mappings)
        
#         start_time = time.time()
#         total_records = len(records)
#         imported = 0
        
#         # Bulk insert
#         for i in range(0, total_records, batch_size):
#             batch = records[i:i+batch_size]
#             bulk_data = []
            
#             for record in batch:
#                 # Clean any problematic fields for ES
#                 clean_record = record.copy()
#                 # Ensure timestamp is in proper format
#                 if 'timestamp' in clean_record:
#                     try:
#                         datetime.fromisoformat(clean_record['timestamp'])
#                     except ValueError:
#                         clean_record['timestamp'] = datetime.now().isoformat()
                
#                 # Add index action
#                 bulk_data.append({"index": {"_index": "logs"}})
#                 bulk_data.append(clean_record)
            
#             if bulk_data:
#                 try:
#                     response = es.bulk(body=bulk_data)
#                     if response.get('errors'):
#                         print(f"Some errors occurred in bulk insert")
#                 except Exception as e:
#                     print(f"Error in bulk insert: {str(e)}")
#                     # Try individual inserts
#                     for j in range(0, len(batch)):
#                         try:
#                             es.index(index="logs", body=batch[j])
#                         except Exception as inner_e:
#                             print(f"Error indexing single record: {str(inner_e)}")
            
#             imported += len(batch)
#             print(f"Elasticsearch: Imported {imported}/{total_records} records")
        
#         end_time = time.time()
#         duration = end_time - start_time
        
#         return {
#             "database": "Elasticsearch",
#             "total_records": total_records,
#             "duration_seconds": duration,
#             "records_per_second": total_records / duration if duration > 0 else 0
#         }
#     except Exception as e:
#         print(f"Error importing to Elasticsearch: {str(e)}")
#         return {
#             "database": "Elasticsearch",
#             "error": str(e)
#         }
    
# def run_elasticsearch_queries(num_queries=20, query_types=None, log_levels=None):
#     """Run query performance tests on Elasticsearch"""
#     if query_types is None:
#         query_types = ["level_filter", "time_range", "complex_query"]
    
#     if log_levels is None:
#         log_levels = ["INFO", "WARNING", "ERROR"]
    
#     results = []
    
#     try:
#         # Connect to Elasticsearch
#         print("Connecting to Elasticsearch for queries...")
#         es = Elasticsearch(["http://elasticsearch:9200"])
        
#         # Check connection
#         if not es.ping():
#             print("Cannot connect to Elasticsearch for queries! Please check if it's running.")
#             return [{
#                 "database": "Elasticsearch",
#                 "error": "Failed to connect to Elasticsearch"
#             }]
        
#         print("Elasticsearch connection successful for queries")
        
#         # Check if index exists
#         if not es.indices.exists(index="logs"):
#             print("Elasticsearch index 'logs' does not exist. Cannot run queries.")
#             return [{
#                 "database": "Elasticsearch",
#                 "error": "Index 'logs' does not exist"
#             }]
        
#         print("Running Elasticsearch queries...")
#         # Run different types of queries
#         for query_type in query_types:
#             times = []
            
#             for _ in range(num_queries):
#                 if query_type == "level_filter":
#                     level = random.choice(log_levels)
#                     start_time = time.time()
#                     try:
#                         es.search(index="logs", body={
#                             "query": {
#                                 "term": {
#                                     "level.keyword": level  # Use .keyword for exact matches
#                                 }
#                             },
#                             "size": 0  # Just count, don't return documents
#                         })
#                         times.append(time.time() - start_time)
#                     except Exception as e:
#                         print(f"Elasticsearch level_filter query error: {e}")
                        
#                 elif query_type == "time_range":
#                     hours = random.choice([1, 6, 24, 48])
#                     threshold = datetime.now().timestamp() - (hours * 3600)
#                     threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
#                     start_time = time.time()
#                     try:
#                         es.search(index="logs", body={
#                             "query": {
#                                 "range": {
#                                     "timestamp": {
#                                         "gt": threshold_iso
#                                     }
#                                 }
#                             },
#                             "size": 0
#                         })
#                         times.append(time.time() - start_time)
#                     except Exception as e:
#                         print(f"Elasticsearch time_range query error: {e}")
                        
#                 elif query_type == "complex_query":
#                     level = random.choice(log_levels)
#                     hours = random.choice([1, 6, 24, 48])
#                     threshold = datetime.now().timestamp() - (hours * 3600)
#                     threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
#                     start_time = time.time()
#                     try:
#                         es.search(index="logs", body={
#                             "query": {
#                                 "bool": {
#                                     "must": [
#                                         {"term": {"level.keyword": level}},  # Use .keyword
#                                         {"range": {"timestamp": {"gt": threshold_iso}}},
#                                         {"match": {"message": "test"}}
#                                     ]
#                                 }
#                             },
#                             "size": 0
#                         })
#                         times.append(time.time() - start_time)
#                     except Exception as e:
#                         print(f"Elasticsearch complex_query error: {e}")
            
#             # Calculate average (only if we have times)
#             if times:
#                 avg_time = sum(times) / len(times)
#                 results.append({
#                     "database": "Elasticsearch",
#                     "query_type": query_type,
#                     "avg_duration_seconds": avg_time
#                 })
#                 print(f"Elasticsearch {query_type} average time: {avg_time:.6f}s")
#             else:
#                 print(f"No successful Elasticsearch queries for {query_type}")
#                 results.append({
#                     "database": "Elasticsearch",
#                     "query_type": query_type,
#                     "error": "No successful queries"
#                 })
        
#     except Exception as e:
#         print(f"Error running Elasticsearch queries: {str(e)}")
#         results.append({
#             "database": "Elasticsearch",
#             "error": str(e)
#         })
    
#     return results

# # def run_query_tests(num_queries=20):
# #     """Run query performance tests on all databases"""
# #     results = []
    
# #     # Define test queries
# #     query_types = [
# #         "level_filter",
# #         "time_range",
# #         "complex_query"
# #     ]
    
# #     # Prepare test data
# #     log_levels = ["INFO", "WARNING", "ERROR"]
# #     time_periods = [
# #         {"hours": 1},
# #         {"hours": 24},
# #         {"days": 7}
# #     ]
    
# #     # PostgreSQL queries
# #     try:
# #         # conn = psycopg2.connect(
# #         #     host="localhost",
# #         #     database="taskdb",
# #         #     user="devops",
# #         #     password="devops_password"
# #         # )

# #         conn = psycopg2.connect(
# #             host="postgres-db",  # Use the service name from docker-compose
# #             database="taskdb",
# #             user="devops",
# #             password="devops_password"
# #         )
# #         cursor = conn.cursor()
        
# #         # Run different types of queries
# #         for query_type in query_types:
# #             times = []
            
# #             for _ in range(num_queries):
# #                 if query_type == "level_filter":
# #                     level = random.choice(log_levels)
# #                     start_time = time.time()
# #                     cursor.execute("SELECT COUNT(*) FROM logs WHERE level = %s", (level,))
# #                     cursor.fetchone()
# #                     times.append(time.time() - start_time)
                    
# #                 elif query_type == "time_range":
# #                     hours = random.choice([1, 6, 24, 48])
# #                     start_time = time.time()
# #                     cursor.execute(
# #                         "SELECT COUNT(*) FROM logs WHERE timestamp > NOW() - INTERVAL '%s hours'", 
# #                         (hours,)
# #                     )
# #                     cursor.fetchone()
# #                     times.append(time.time() - start_time)
                    
# #                 elif query_type == "complex_query":
# #                     level = random.choice(log_levels)
# #                     hours = random.choice([1, 6, 24, 48])
# #                     message_pattern = "%test%"
                    
# #                     start_time = time.time()
# #                     cursor.execute(
# #                         """
# #                         SELECT COUNT(*) FROM logs 
# #                         WHERE level = %s 
# #                         AND timestamp > NOW() - INTERVAL '%s hours'
# #                         AND message LIKE %s
# #                         """,
# #                         (level, hours, message_pattern)
# #                     )
# #                     cursor.fetchone()
# #                     times.append(time.time() - start_time)
            
# #             # Calculate average
# #             avg_time = sum(times) / len(times) if times else 0
# #             results.append({
# #                 "database": "PostgreSQL",
# #                 "query_type": query_type,
# #                 "avg_duration_seconds": avg_time
# #             })
        
# #         cursor.close()
# #         conn.close()
# #     except Exception as e:
# #         print(f"Error running PostgreSQL queries: {str(e)}")
# #         results.append({
# #             "database": "PostgreSQL",
# #             "error": str(e)
# #         })
    
# #     # MongoDB queries
# #     try:
# #         # client = pymongo.MongoClient(
# #         #     "mongodb://devops:devops_password@localhost:27017/admin"
# #         # )

# #         client = pymongo.MongoClient(
# #             "mongodb://devops:devops_password@mongodb:27017/admin"  # Use the service name
# #         )
# #         db = client.logs
# #         collection = db.app_logs
        
# #         # Run different types of queries
# #         for query_type in query_types:
# #             times = []
            
# #             for _ in range(num_queries):
# #                 if query_type == "level_filter":
# #                     level = random.choice(log_levels)
# #                     start_time = time.time()
# #                     collection.count_documents({"level": level})
# #                     times.append(time.time() - start_time)
                    
# #                 elif query_type == "time_range":
# #                     hours = random.choice([1, 6, 24, 48])
# #                     threshold = datetime.now().timestamp() - (hours * 3600)
# #                     threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
# #                     start_time = time.time()
# #                     collection.count_documents({"timestamp": {"$gt": threshold_iso}})
# #                     times.append(time.time() - start_time)
                    
# #                 elif query_type == "complex_query":
# #                     level = random.choice(log_levels)
# #                     hours = random.choice([1, 6, 24, 48])
# #                     threshold = datetime.now().timestamp() - (hours * 3600)
# #                     threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
# #                     start_time = time.time()
# #                     collection.count_documents({
# #                         "level": level,
# #                         "timestamp": {"$gt": threshold_iso},
# #                         "message": {"$regex": "test"}
# #                     })
# #                     times.append(time.time() - start_time)
            
# #             # Calculate average
# #             avg_time = sum(times) / len(times) if times else 0
# #             results.append({
# #                 "database": "MongoDB",
# #                 "query_type": query_type,
# #                 "avg_duration_seconds": avg_time
# #             })
        
# #         client.close()
# #     except Exception as e:
# #         print(f"Error running MongoDB queries: {str(e)}")
# #         results.append({
# #             "database": "MongoDB",
# #             "error": str(e)
# #         })
    
# #     # Elasticsearch queries
# #     try:
# #         from elasticsearch import Elasticsearch
# #         # es = Elasticsearch(["http://localhost:9200"])
# #         es = Elasticsearch(["http://elasticsearch:9200"])  # Use the service name        
# #         # Check connection
# #         if not es.ping():
# #             print("Cannot connect to Elasticsearch for queries! Please check if it's running.")
# #             results.append({
# #                 "database": "Elasticsearch",
# #                 "error": "Failed to connect to Elasticsearch"
# #             })
# #         else:
# #             # Run different types of queries
# #             for query_type in query_types:
# #                 times = []
                
# #                 for _ in range(num_queries):
# #                     if query_type == "level_filter":
# #                         level = random.choice(log_levels)
# #                         start_time = time.time()
# #                         es.count(index="logs", body={"query": {"term": {"level": level}}})
# #                         times.append(time.time() - start_time)
                        
# #                     elif query_type == "time_range":
# #                         hours = random.choice([1, 6, 24, 48])
# #                         threshold = datetime.now().timestamp() - (hours * 3600)
# #                         threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                        
# #                         start_time = time.time()
# #                         es.count(index="logs", body={
# #                             "query": {
# #                                 "range": {
# #                                     "timestamp": {
# #                                         "gt": threshold_iso
# #                                     }
# #                                 }
# #                             }
# #                         })
# #                         times.append(time.time() - start_time)
                        
# #                     elif query_type == "complex_query":
# #                         level = random.choice(log_levels)
# #                         hours = random.choice([1, 6, 24, 48])
# #                         threshold = datetime.now().timestamp() - (hours * 3600)
# #                         threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                        
# #                         start_time = time.time()
# #                         es.count(index="logs", body={
# #                             "query": {
# #                                 "bool": {
# #                                     "must": [
# #                                         {"term": {"level": level}},
# #                                         {"range": {"timestamp": {"gt": threshold_iso}}},
# #                                         {"match": {"message": "test"}}
# #                                     ]
# #                                 }
# #                             }
# #                         })
# #                         times.append(time.time() - start_time)
                
# #                 # Calculate average
# #                 avg_time = sum(times) / len(times) if times else 0
# #                 results.append({
# #                     "database": "Elasticsearch",
# #                     "query_type": query_type,
# #                     "avg_duration_seconds": avg_time
# #                 })
# #     except Exception as e:
# #         print(f"Error running Elasticsearch queries: {str(e)}")
# #         results.append({
# #             "database": "Elasticsearch",
# #             "error": str(e)
# #         })
    
# #     return results

# # def main():
# #     parser = argparse.ArgumentParser(description='Import logs to different databases and run performance tests')
# #     parser.add_argument('--file', required=True, help='Path to JSON log file')
# #     parser.add_argument('--queries', type=int, default=20, help='Number of queries to run for testing')
# #     args = parser.parse_args()
    
# #     # Read log records
# #     print(f"Reading log records from {args.file}...")
# #     records = read_log_file(args.file)
# #     if not records:
# #         print("No records found. Exiting.")
# #         return
# #     print(f"Read {len(records)} log records.")
    
# #     # Import to PostgreSQL
# #     print("\nImporting to PostgreSQL...")
# #     pg_results = import_to_postgres(records)
# #     print(f"PostgreSQL import completed in {pg_results.get('duration_seconds', 'N/A')} seconds")
    
# #     # Import to MongoDB
# #     print("\nImporting to MongoDB...")
# #     mongo_results = import_to_mongodb(records)
# #     print(f"MongoDB import completed in {mongo_results.get('duration_seconds', 'N/A')} seconds")
    
# #     # Import to Elasticsearch
# #     print("\nImporting to Elasticsearch...")
# #     es_results = import_to_elasticsearch(records)
# #     print(f"Elasticsearch import completed in {es_results.get('duration_seconds', 'N/A')} seconds")
    
# #     # Run query tests
# #     print("\nRunning query performance tests...")
# #     query_results = run_query_tests(args.queries)
    
# #     # Combine results
# #     all_results = {
# #         "import_performance": [pg_results, mongo_results, es_results],
# #         "query_performance": query_results
# #     }
    
# #     # Save results to file
# #     output_file = "performance_results.json"
# #     with open(output_file, 'w') as f:
# #         json.dump(all_results, f, indent=2)
    
# #     print(f"\nResults saved to {output_file}")
    
# #     # Print summary
# #     print("\nPerformance Summary:")
# #     print("====================")
# #     print("\nImport Performance:")
# #     for result in [pg_results, mongo_results, es_results]:
# #         db = result.get("database")
# #         duration = result.get("duration_seconds", "N/A")
# #         rps = result.get("records_per_second", "N/A")
        
# #         # Handle the case where duration or rps might be strings
# #         if isinstance(duration, str) or isinstance(rps, str):
# #             print(f"  {db}: {duration}s, {rps} records/s")
# #         else:
# #             print(f"  {db}: {duration:.2f}s, {rps:.2f} records/s")
    
# #     print("\nQuery Performance (Average in seconds):")
# #     for query_type in ["level_filter", "time_range", "complex_query"]:
# #         print(f"\n  {query_type}:")
# #         for db in ["PostgreSQL", "MongoDB", "Elasticsearch"]:
# #             results = [r for r in query_results if r.get("database") == db and r.get("query_type") == query_type]
# #             if results:
# #                 avg_time = results[0].get("avg_duration_seconds", "N/A")
# #                 if isinstance(avg_time, str):
# #                     print(f"    {db}: {avg_time}s")
# #                 else:
# #                     print(f"    {db}: {avg_time:.6f}s")


# def run_query_tests(num_queries=20):
#     """Run query performance tests on all databases"""
#     results = []
    
#     # Define test queries
#     query_types = [
#         "level_filter",
#         "time_range",
#         "complex_query"
#     ]
    
#     # Prepare test data
#     log_levels = ["INFO", "WARNING", "ERROR"]
    
#     # PostgreSQL queries
#     try:
#         conn = psycopg2.connect(
#             host="postgres-db",  # Use the service name from docker-compose
#             database="taskdb",
#             user="devops",
#             password="devops_password"
#         )
#         cursor = conn.cursor()
        
#         print("Running PostgreSQL queries...")
#         # Run different types of queries
#         for query_type in query_types:
#             times = []
            
#             for _ in range(num_queries):
#                 if query_type == "level_filter":
#                     level = random.choice(log_levels)
#                     start_time = time.time()
#                     cursor.execute("SELECT COUNT(*) FROM logs WHERE level = %s", (level,))
#                     cursor.fetchone()
#                     times.append(time.time() - start_time)
                    
#                 elif query_type == "time_range":
#                     hours = random.choice([1, 6, 24, 48])
#                     start_time = time.time()
#                     cursor.execute(
#                         "SELECT COUNT(*) FROM logs WHERE timestamp > NOW() - INTERVAL '%s hours'", 
#                         (hours,)
#                     )
#                     cursor.fetchone()
#                     times.append(time.time() - start_time)
                    
#                 elif query_type == "complex_query":
#                     level = random.choice(log_levels)
#                     hours = random.choice([1, 6, 24, 48])
#                     message_pattern = "%test%"
                    
#                     start_time = time.time()
#                     cursor.execute(
#                         """
#                         SELECT COUNT(*) FROM logs 
#                         WHERE level = %s 
#                         AND timestamp > NOW() - INTERVAL '%s hours'
#                         AND message LIKE %s
#                         """,
#                         (level, hours, message_pattern)
#                     )
#                     cursor.fetchone()
#                     times.append(time.time() - start_time)
            
#             # Calculate average
#             avg_time = sum(times) / len(times) if times else 0
#             results.append({
#                 "database": "PostgreSQL",
#                 "query_type": query_type,
#                 "avg_duration_seconds": avg_time
#             })
#             print(f"PostgreSQL {query_type} average time: {avg_time:.6f}s")
        
#         cursor.close()
#         conn.close()
#     except Exception as e:
#         print(f"Error running PostgreSQL queries: {str(e)}")
#         results.append({
#             "database": "PostgreSQL",
#             "error": str(e)
#         })
    
#     # MongoDB queries
#     try:
#         client = pymongo.MongoClient(
#             "mongodb://devops:devops_password@mongodb:27017/admin"  # Use the service name
#         )
#         db = client.logs
#         collection = db.app_logs
        
#         print("Running MongoDB queries...")
#         # Run different types of queries
#         for query_type in query_types:
#             times = []
            
#             for _ in range(num_queries):
#                 if query_type == "level_filter":
#                     level = random.choice(log_levels)
#                     start_time = time.time()
#                     collection.count_documents({"level": level})
#                     times.append(time.time() - start_time)
                    
#                 elif query_type == "time_range":
#                     hours = random.choice([1, 6, 24, 48])
#                     threshold = datetime.now().timestamp() - (hours * 3600)
#                     threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
#                     start_time = time.time()
#                     collection.count_documents({"timestamp": {"$gt": threshold_iso}})
#                     times.append(time.time() - start_time)
                    
#                 elif query_type == "complex_query":
#                     level = random.choice(log_levels)
#                     hours = random.choice([1, 6, 24, 48])
#                     threshold = datetime.now().timestamp() - (hours * 3600)
#                     threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
#                     start_time = time.time()
#                     collection.count_documents({
#                         "level": level,
#                         "timestamp": {"$gt": threshold_iso},
#                         "message": {"$regex": "test"}
#                     })
#                     times.append(time.time() - start_time)
            
#             # Calculate average
#             avg_time = sum(times) / len(times) if times else 0
#             results.append({
#                 "database": "MongoDB",
#                 "query_type": query_type,
#                 "avg_duration_seconds": avg_time
#             })
#             print(f"MongoDB {query_type} average time: {avg_time:.6f}s")
        
#         client.close()
#     except Exception as e:
#         print(f"Error running MongoDB queries: {str(e)}")
#         results.append({
#             "database": "MongoDB",
#             "error": str(e)
#         })
    
#     # Run Elasticsearch queries using the dedicated function
#     es_results = run_elasticsearch_queries(num_queries, query_types, log_levels)
#     results.extend(es_results)
    
#     return results

# def main():
#     parser = argparse.ArgumentParser(description='Import logs to different databases and run performance tests')
#     parser.add_argument('--file', required=True, help='Path to JSON log file')
#     parser.add_argument('--queries', type=int, default=20, help='Number of queries to run for testing')
#     parser.add_argument('--skip-import', action='store_true', help='Skip import phase, run only queries')
#     args = parser.parse_args()
    
#     all_results = {}
    
#     if not args.skip_import:
#         # Read log records
#         print(f"Reading log records from {args.file}...")
#         records = read_log_file(args.file)
#         if not records:
#             print("No records found. Exiting.")
#             return
#         print(f"Read {len(records)} log records.")
        
#         # Import to PostgreSQL
#         print("\nImporting to PostgreSQL...")
#         pg_results = import_to_postgres(records)
#         print(f"PostgreSQL import completed in {pg_results.get('duration_seconds', 'N/A')} seconds")
        
#         # Import to MongoDB
#         print("\nImporting to MongoDB...")
#         mongo_results = import_to_mongodb(records)
#         print(f"MongoDB import completed in {mongo_results.get('duration_seconds', 'N/A')} seconds")
        
#         # Import to Elasticsearch
#         print("\nImporting to Elasticsearch...")
#         es_results = import_to_elasticsearch(records)
#         print(f"Elasticsearch import completed in {es_results.get('duration_seconds', 'N/A')} seconds")
        
#         all_results["import_performance"] = [pg_results, mongo_results, es_results]
#     else:
#         print("Skipping import phase as requested.")
    
#     # Run query tests
#     print("\nRunning query performance tests...")
#     query_results = run_query_tests(args.queries)
#     all_results["query_performance"] = query_results
    
#     # Save results to file
#     output_file = "performance_results.json"
#     with open(output_file, 'w') as f:
#         json.dump(all_results, f, indent=2)
    
#     print(f"\nResults saved to {output_file}")
    
#     # Print summary
#     print("\nPerformance Summary:")
#     print("====================")
    
#     if "import_performance" in all_results:
#         print("\nImport Performance:")
#         for result in all_results["import_performance"]:
#             db = result.get("database")
#             duration = result.get("duration_seconds", "N/A")
#             rps = result.get("records_per_second", "N/A")
            
#             # Handle the case where duration or rps might be strings
#             if isinstance(duration, str) or isinstance(rps, str):
#                 print(f"  {db}: {duration}s, {rps} records/s")
#             else:
#                 print(f"  {db}: {duration:.2f}s, {rps:.2f} records/s")
    
#     print("\nQuery Performance (Average in seconds):")
#     for query_type in ["level_filter", "time_range", "complex_query"]:
#         print(f"\n  {query_type}:")
#         for db in ["PostgreSQL", "MongoDB", "Elasticsearch"]:
#             results = [r for r in query_results if r.get("database") == db and r.get("query_type") == query_type]
#             if results:
#                 if "error" in results[0]:
#                     print(f"    {db}: ERROR - {results[0].get('error')}")
#                 else:
#                     avg_time = results[0].get("avg_duration_seconds", "N/A")
#                     if isinstance(avg_time, str):
#                         print(f"    {db}: {avg_time}s")
#                     else:
#                         print(f"    {db}: {avg_time:.6f}s")
#             else:
#                 print(f"    {db}: No results")

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
Database comparison tool for log imports and queries.
This script imports logs into PostgreSQL, MongoDB, and Elasticsearch,
then runs benchmark queries to compare performance.
"""
import argparse
import json
import os
import time
import random
import psutil
from datetime import datetime, timedelta

# Import database libraries
import psycopg2
import pymongo
from elasticsearch import Elasticsearch

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Import logs and benchmark database performance')
    parser.add_argument('--file', default='logs/test_logs.json', help='Log file to import')
    parser.add_argument('--queries', type=int, default=10, help='Number of queries to execute for benchmarking')
    parser.add_argument('--output', default='performance_results.json', help='Output file for performance results')
    return parser.parse_args()

def load_logs(file_path):
    """Load logs from JSON file"""
    if not os.path.exists(file_path):
        print(f"Error: Log file {file_path} not found")
        return []
        
    with open(file_path, 'r') as f:
        return json.load(f)

def record_resource_metrics(db_type, operation, metrics_file="resource_metrics.json"):
    """Record system resource metrics before database operations"""
    metrics = {
        "db_type": db_type,
        "operation": operation,
        "timestamp": datetime.now().isoformat(),
        "before": {},
        "after": {},
        "duration_seconds": 0
    }
    
    # Record before metrics
    process = psutil.Process(os.getpid())
    metrics["before"]["cpu_percent"] = psutil.cpu_percent(interval=0.1)
    metrics["before"]["memory_percent"] = process.memory_percent()
    metrics["before"]["memory_mb"] = process.memory_info().rss / (1024 * 1024)
    
    if db_type == "postgres":
        disk_usage = psutil.disk_usage('/var/lib/postgresql/data' if os.path.exists('/var/lib/postgresql/data') else '/')
    elif db_type == "mongodb":
        disk_usage = psutil.disk_usage('/data/db' if os.path.exists('/data/db') else '/')
    elif db_type == "elasticsearch":
        disk_usage = psutil.disk_usage('/usr/share/elasticsearch/data' if os.path.exists('/usr/share/elasticsearch/data') else '/')
    else:
        disk_usage = psutil.disk_usage('/')
        
    metrics["before"]["disk_used_gb"] = disk_usage.used / (1024**3)
    metrics["before"]["disk_free_gb"] = disk_usage.free / (1024**3)
    
    start_time = time.time()
    
    return metrics, start_time

def update_resource_metrics(metrics, start_time, metrics_file="resource_metrics.json"):
    """Update metrics with after values and save to file"""
    # Record after metrics
    process = psutil.Process(os.getpid())
    metrics["after"]["cpu_percent"] = psutil.cpu_percent(interval=0.1)
    metrics["after"]["memory_percent"] = process.memory_percent()
    metrics["after"]["memory_mb"] = process.memory_info().rss / (1024 * 1024)
    
    if metrics["db_type"] == "postgres":
        disk_usage = psutil.disk_usage('/var/lib/postgresql/data' if os.path.exists('/var/lib/postgresql/data') else '/')
    elif metrics["db_type"] == "mongodb":
        disk_usage = psutil.disk_usage('/data/db' if os.path.exists('/data/db') else '/')
    elif metrics["db_type"] == "elasticsearch":
        disk_usage = psutil.disk_usage('/usr/share/elasticsearch/data' if os.path.exists('/usr/share/elasticsearch/data') else '/')
    else:
        disk_usage = psutil.disk_usage('/')
        
    metrics["after"]["disk_used_gb"] = disk_usage.used / (1024**3)
    metrics["after"]["disk_free_gb"] = disk_usage.free / (1024**3)
    
    # Calculate duration
    metrics["duration_seconds"] = time.time() - start_time
    
    # Load existing metrics if file exists
    all_metrics = []
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, 'r') as f:
                all_metrics = json.load(f)
        except:
            all_metrics = []
    
    # Add new metrics
    all_metrics.append(metrics)
    
    # Write to file
    with open(metrics_file, 'w') as f:
        json.dump(all_metrics, f, indent=2)
    
    return metrics

def import_to_postgres(logs):
    """Import logs to PostgreSQL database"""
    postgres_metrics, start_time = record_resource_metrics("postgres", "import")
    
    # Connect to PostgreSQL
    conn = None
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="taskmanager",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Create logs table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP,
            level VARCHAR(20),
            message TEXT,
            source VARCHAR(100),
            tags JSONB
        )
        """)
        conn.commit()
        
        # Import logs
        print(f"Importing {len(logs)} logs to PostgreSQL...")
        for log in logs:
            cursor.execute("""
            INSERT INTO logs (timestamp, level, message, source, tags)
            VALUES (%s, %s, %s, %s, %s)
            """, (
                log.get('timestamp', datetime.now().isoformat()),
                log.get('level', 'INFO'),
                log.get('message', ''),
                log.get('source', 'app'),
                json.dumps(log.get('tags', {}))
            ))
        
        conn.commit()
        print("PostgreSQL import completed")
        
    except Exception as e:
        print(f"PostgreSQL import error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    
    # Update and return metrics
    postgres_metrics = update_resource_metrics(postgres_metrics, start_time)
    print(f"PostgreSQL import completed in {postgres_metrics['duration_seconds']:.2f} seconds")
    
    return postgres_metrics['duration_seconds']

def import_to_mongodb(logs):
    """Import logs to MongoDB database"""
    mongodb_metrics, start_time = record_resource_metrics("mongodb", "import")
    
    # Connect to MongoDB
    client = None
    try:
        print("Connecting to MongoDB...")
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["taskmanager"]
        logs_collection = db["logs"]
        
        # Import logs
        print(f"Importing {len(logs)} logs to MongoDB...")
        documents = []
        for log in logs:
            # Convert timestamp string to datetime object if possible
            timestamp = log.get('timestamp', datetime.now().isoformat())
            try:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
                
            documents.append({
                'timestamp': timestamp,
                'level': log.get('level', 'INFO'),
                'message': log.get('message', ''),
                'source': log.get('source', 'app'),
                'tags': log.get('tags', {})
            })
        
        # Insert in bulk for better performance
        if documents:
            logs_collection.insert_many(documents)
        
        print("MongoDB import completed")
        
    except Exception as e:
        print(f"MongoDB import error: {e}")
    finally:
        if client:
            client.close()
    
    # Update and return metrics
    mongodb_metrics = update_resource_metrics(mongodb_metrics, start_time)
    print(f"MongoDB import completed in {mongodb_metrics['duration_seconds']:.2f} seconds")
    
    return mongodb_metrics['duration_seconds']

def import_to_elasticsearch(logs):
    """Import logs to Elasticsearch database"""
    elasticsearch_metrics, start_time = record_resource_metrics("elasticsearch", "import")
    
    # Connect to Elasticsearch
    es = None
    try:
        print("Connecting to Elasticsearch...")
        es = Elasticsearch(["http://localhost:9200"])
        
        # Create index if it doesn't exist
        if not es.indices.exists(index="logs"):
            es.indices.create(index="logs", body={
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "message": {"type": "text"},
                        "source": {"type": "keyword"},
                        "tags": {"type": "object"}
                    }
                }
            })
        
        # Import logs
        print(f"Importing {len(logs)} logs to Elasticsearch...")
        for i, log in enumerate(logs):
            # Convert timestamp string to datetime object if possible
            timestamp = log.get('timestamp', datetime.now().isoformat())
            try:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                
            es.index(index="logs", body={
                'timestamp': timestamp,
                'level': log.get('level', 'INFO'),
                'message': log.get('message', ''),
                'source': log.get('source', 'app'),
                'tags': log.get('tags', {})
            })
            
            # Print progress for larger imports
            if (i+1) % 1000 == 0:
                print(f"Imported {i+1} logs to Elasticsearch...")
        
        # Refresh index to make new documents available for search
        es.indices.refresh(index="logs")
        print("Elasticsearch import completed")
        
    except Exception as e:
        print(f"Elasticsearch import error: {e}")
    
    # Update and return metrics
    elasticsearch_metrics = update_resource_metrics(elasticsearch_metrics, start_time)
    print(f"Elasticsearch import completed in {elasticsearch_metrics['duration_seconds']:.2f} seconds")
    
    return elasticsearch_metrics['duration_seconds']

def benchmark_postgres_queries(num_queries):
    """Run benchmark queries on PostgreSQL"""
    postgres_metrics, start_time = record_resource_metrics("postgres", "query")
    
    query_times = []
    
    # Connect to PostgreSQL
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="taskmanager",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        print(f"Running {num_queries} benchmark queries on PostgreSQL...")
        
        # Get total log count
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]
        
        # Run random level filter queries
        levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        for i in range(num_queries):
            # Pick a random level
            level = random.choice(levels)
            
            start = time.time()
            cursor.execute("SELECT * FROM logs WHERE level = %s LIMIT 100", (level,))
            rows = cursor.fetchall()
            end = time.time()
            
            query_times.append((end - start) * 1000)  # Convert to ms
            print(f"PostgreSQL query {i+1}: {query_times[-1]:.2f} ms, {len(rows)} results")
        
    except Exception as e:
        print(f"PostgreSQL query error: {e}")
    finally:
        if conn:
            conn.close()
    
    # Calculate average query time
    avg_query_time = sum(query_times) / len(query_times) if query_times else 0
    print(f"PostgreSQL average query time: {avg_query_time:.2f} ms")
    
    # Update and return metrics
    postgres_metrics = update_resource_metrics(postgres_metrics, start_time)
    
    return avg_query_time

def benchmark_mongodb_queries(num_queries):
    """Run benchmark queries on MongoDB"""
    mongodb_metrics, start_time = record_resource_metrics("mongodb", "query")
    
    query_times = []
    
    # Connect to MongoDB
    client = None
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["taskmanager"]
        logs_collection = db["logs"]
        
        print(f"Running {num_queries} benchmark queries on MongoDB...")
        
        # Get total log count
        total_logs = logs_collection.count_documents({})
        
        # Run random level filter queries
        levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        for i in range(num_queries):
            # Pick a random level
            level = random.choice(levels)
            
            start = time.time()
            cursor = logs_collection.find({"level": level}).limit(100)
            rows = list(cursor)
            end = time.time()
            
            query_times.append((end - start) * 1000)  # Convert to ms
            print(f"MongoDB query {i+1}: {query_times[-1]:.2f} ms, {len(rows)} results")
        
    except Exception as e:
        print(f"MongoDB query error: {e}")
    finally:
        if client:
            client.close()
    
    # Calculate average query time
    avg_query_time = sum(query_times) / len(query_times) if query_times else 0
    print(f"MongoDB average query time: {avg_query_time:.2f} ms")
    
    # Update and return metrics
    mongodb_metrics = update_resource_metrics(mongodb_metrics, start_time)
    
    return avg_query_time

def benchmark_elasticsearch_queries(num_queries):
    """Run benchmark queries on Elasticsearch"""
    elasticsearch_metrics, start_time = record_resource_metrics("elasticsearch", "query")
    
    query_times = []
    
    # Connect to Elasticsearch
    try:
        es = Elasticsearch(["http://localhost:9200"])
        
        print(f"Running {num_queries} benchmark queries on Elasticsearch...")
        
        # Get total log count
        total_logs = es.count(index="logs")["count"]
        
        # Run random level filter queries
        levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        for i in range(num_queries):
            # Pick a random level
            level = random.choice(levels)
            
            start = time.time()
            result = es.search(index="logs", body={
                "query": {
                    "match": {
                        "level": level
                    }
                },
                "size": 100
            })
            end = time.time()
            
            query_times.append((end - start) * 1000)  # Convert to ms
            print(f"Elasticsearch query {i+1}: {query_times[-1]:.2f} ms, {len(result['hits']['hits'])} results")
        
    except Exception as e:
        print(f"Elasticsearch query error: {e}")
    
    # Calculate average query time
    avg_query_time = sum(query_times) / len(query_times) if query_times else 0
    print(f"Elasticsearch average query time: {avg_query_time:.2f} ms")
    
    # Update and return metrics
    elasticsearch_metrics = update_resource_metrics(elasticsearch_metrics, start_time)
    
    return avg_query_time

def main():
    """Main function"""
    args = parse_args()
    
    # Load logs from file
    logs = load_logs(args.file)
    if not logs:
        print("No logs to import. Exiting.")
        return
    
    print(f"Loaded {len(logs)} logs from {args.file}")
    
    # Import logs to each database
    postgres_import_time = import_to_postgres(logs)
    mongodb_import_time = import_to_mongodb(logs)
    elasticsearch_import_time = import_to_elasticsearch(logs)
    
    # Run benchmark queries
    postgres_query_time = benchmark_postgres_queries(args.queries)
    mongodb_query_time = benchmark_mongodb_queries(args.queries)
    elasticsearch_query_time = benchmark_elasticsearch_queries(args.queries)
    
    # Compile performance results
    results = {
        "import_performance": {
            "postgres": postgres_import_time,
            "mongodb": mongodb_import_time,
            "elasticsearch": elasticsearch_import_time
        },
        "query_performance": {
            "postgres": postgres_query_time,
            "mongodb": mongodb_query_time,
            "elasticsearch": elasticsearch_query_time
        }
    }
    
    # Save results to file
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Performance results saved to {args.output}")
    
    # Print summary
    print("\n==== Database Performance Summary ====")
    print("\nImport Performance (seconds):")
    print(f"PostgreSQL: {postgres_import_time:.2f}")
    print(f"MongoDB: {mongodb_import_time:.2f}")
    print(f"Elasticsearch: {elasticsearch_import_time:.2f}")
    
    print("\nQuery Performance (milliseconds):")
    print(f"PostgreSQL: {postgres_query_time:.2f}")
    print(f"MongoDB: {mongodb_query_time:.2f}")
    print(f"Elasticsearch: {elasticsearch_query_time:.2f}")
    
    # Determine fastest database
    fastest_import = min(
        ("PostgreSQL", postgres_import_time),
        ("MongoDB", mongodb_import_time),
        ("Elasticsearch", elasticsearch_import_time),
        key=lambda x: x[1]
    )
    
    fastest_query = min(
        ("PostgreSQL", postgres_query_time),
        ("MongoDB", mongodb_query_time),
        ("Elasticsearch", elasticsearch_query_time),
        key=lambda x: x[1]
    )
    
    print(f"\nFastest Import: {fastest_import[0]} ({fastest_import[1]:.2f} seconds)")
    print(f"Fastest Query: {fastest_query[0]} ({fastest_query[1]:.2f} ms)")

if __name__ == "__main__":
    main()