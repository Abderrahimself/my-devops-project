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
import os
import json
import time
import argparse
import psycopg2
from datetime import datetime
import pymongo
from elasticsearch import Elasticsearch
import random
import glob
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(_name_)

def read_log_file(file_path, format_type="json"):
    """Read log records from log file with specified format"""
    records = []
    try:
        if format_type == "json":
            # Process JSON log file
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        records.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in line: {line[:50]}...")
                        continue
                        
        elif format_type == "text":
            # Process traditional text log file
            # This is a simple example - you'd need to adapt this to your actual log format
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        # Example format: "2025-04-09 12:00:00 [INFO] module.function:123 - Test log message"
                        parts = line.strip().split(" - ", 1)
                        if len(parts) != 2:
                            continue
                            
                        header, message = parts
                        header_parts = header.split()
                        
                        if len(header_parts) < 3:
                            continue
                            
                        date_str = header_parts[0]
                        time_str = header_parts[1]
                        level_str = header_parts[2].strip('[]')
                        
                        # Extract module and line info if available
                        module_info = ""
                        line_num = None
                        function_name = None
                        
                        if len(header_parts) > 3:
                            module_info = header_parts[3]
                            if ':' in module_info:
                                module_parts = module_info.split(':')
                                module_info = module_parts[0]
                                if '.' in module_info:
                                    module_parts = module_info.split('.')
                                    module_name = module_parts[0]
                                    function_name = module_parts[1] if len(module_parts) > 1 else None
                                else:
                                    module_name = module_info
                                line_num = int(module_parts[1]) if len(module_parts) > 1 and module_parts[1].isdigit() else None
                            else:
                                module_name = module_info
                        else:
                            module_name = None
                            
                        # Create a structured record
                        record = {
                            "timestamp": f"{date_str}T{time_str}.000Z",
                            "level": level_str,
                            "message": message,
                            "module": module_name,
                            "function": function_name,
                            "line": line_num
                        }
                        records.append(record)
                    except Exception as e:
                        logger.warning(f"Error parsing line: {line[:50]}... - {str(e)}")
                        continue
                        
        elif format_type == "jenkins":
            # Process Jenkins logs
            # Adapt this based on your Jenkins log format
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        # Example format for Jenkins logs
                        if "[Pipeline]" in line or "[JENKINS]" in line:
                            parts = line.strip().split(" ", 3)
                            if len(parts) < 4:
                                continue
                                
                            timestamp_str = parts[0] + " " + parts[1]
                            try:
                                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                timestamp_iso = timestamp.isoformat() + ".000Z"
                            except ValueError:
                                timestamp_iso = datetime.now().isoformat() + ".000Z"
                                
                            level = "INFO"
                            if "ERROR" in line:
                                level = "ERROR"
                            elif "WARNING" in line or "WARN" in line:
                                level = "WARNING"
                                
                            message = parts[3] if len(parts) > 3 else line.strip()
                            
                            # Create record
                            record = {
                                "timestamp": timestamp_iso,
                                "level": level,
                                "message": message,
                                "module": "jenkins",
                                "function": "pipeline",
                                "line": None
                            }
                            records.append(record)
                    except Exception as e:
                        logger.warning(f"Error parsing Jenkins log line: {line[:50]}... - {str(e)}")
                        continue
                        
        return records
    except Exception as e:
        logger.error(f"Error reading log file {file_path}: {str(e)}")
        return []

def collect_logs(sources):
    """Collect logs from multiple sources"""
    all_records = []
    
    for source in sources:
        source_type = source.get("type", "json")
        path_pattern = source.get("path", "")
        
        if not path_pattern:
            continue
            
        # Find all matching files
        matching_files = glob.glob(path_pattern)
        logger.info(f"Found {len(matching_files)} files matching pattern: {path_pattern}")
        
        for file_path in matching_files:
            logger.info(f"Processing {source_type} log file: {file_path}")
            records = read_log_file(file_path, source_type)
            logger.info(f"Read {len(records)} records from {file_path}")
            all_records.extend(records)
            
    logger.info(f"Collected {len(all_records)} total log records from all sources")
    return all_records

def import_to_postgres(records, batch_size=100):
    """Import log records to PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="postgres-db",  # Use the service name from docker-compose
            database="taskdb",
            user="devops",
            password="devops_password"
        )
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE,
            level VARCHAR(20),
            message TEXT,
            module VARCHAR(100),
            function VARCHAR(100),
            line INTEGER,
            request_id VARCHAR(100),
            user_agent TEXT,
            ip VARCHAR(50),
            raw_log JSONB
        )
        """)
        conn.commit()
        
        start_time = time.time()
        total_records = len(records)
        imported = 0
        
        for i in range(0, total_records, batch_size):
            batch = records[i:i+batch_size]
            for record in batch:
                cursor.execute(
                    """
                    INSERT INTO logs 
                    (timestamp, level, message, module, function, line, request_id, user_agent, ip, raw_log)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        datetime.fromisoformat(record.get('timestamp').replace('Z', '+00:00')),
                        record.get('level'),
                        record.get('message'),
                        record.get('module'),
                        record.get('function'),
                        record.get('line'),
                        record.get('request_id'),
                        record.get('user_agent'),
                        record.get('ip'),
                        json.dumps(record)
                    )
                )
            conn.commit()
            imported += len(batch)
            logger.info(f"PostgreSQL: Imported {imported}/{total_records} records")
        
        end_time = time.time()
        duration = end_time - start_time
        
        cursor.close()
        conn.close()
        
        return {
            "database": "PostgreSQL",
            "total_records": total_records,
            "duration_seconds": duration,
            "records_per_second": total_records / duration if duration > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error importing to PostgreSQL: {str(e)}")
        return {
            "database": "PostgreSQL",
            "error": str(e)
        }

def import_to_mongodb(records, batch_size=100):
    """Import log records to MongoDB"""
    try:
        client = pymongo.MongoClient(
            "mongodb://devops:devops_password@mongodb:27017/admin"  # Use the service name
        )
        db = client.logs
        collection = db.app_logs
        
        start_time = time.time()
        total_records = len(records)
        
        # Insert in batches
        for i in range(0, total_records, batch_size):
            batch = records[i:i+batch_size]
            collection.insert_many(batch)
            logger.info(f"MongoDB: Imported {min(i+batch_size, total_records)}/{total_records} records")
        
        end_time = time.time()
        duration = end_time - start_time
        
        client.close()
        
        return {
            "database": "MongoDB",
            "total_records": total_records,
            "duration_seconds": duration,
            "records_per_second": total_records / duration if duration > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error importing to MongoDB: {str(e)}")
        return {
            "database": "MongoDB",
            "error": str(e)
        }

def import_to_elasticsearch(records, batch_size=100):
    """Import log records to Elasticsearch"""
    try:
        # Connect to Elasticsearch
        logger.info("Connecting to Elasticsearch...")
        es = Elasticsearch(["http://elasticsearch:9200"])  # Use the service name
        
        # Check connection
        if not es.ping():
            logger.error("Cannot connect to Elasticsearch! Please check if it's running.")
            return {
                "database": "Elasticsearch",
                "error": "Failed to connect to Elasticsearch"
            }
        
        logger.info("Elasticsearch connection successful")
        
        # Make sure the index exists with proper mappings
        if not es.indices.exists(index="logs"):
            logger.info("Creating 'logs' index with proper mappings...")
            # Define proper mappings for log data
            mappings = {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "message": {"type": "text"},
                        "module": {"type": "keyword"},
                        "function": {"type": "keyword"},
                        "line": {"type": "integer"},
                        "request_id": {"type": "keyword"},
                        "user_agent": {"type": "text"},
                        "ip": {"type": "ip"},
                        "source": {"type": "keyword"}
                    }
                }
            }
            es.indices.create(index="logs", body=mappings)
        
        start_time = time.time()
        total_records = len(records)
        imported = 0
        
        # Bulk insert
        for i in range(0, total_records, batch_size):
            batch = records[i:i+batch_size]
            bulk_data = []
            
            for record in batch:
                # Clean any problematic fields for ES
                clean_record = record.copy()
                # Ensure timestamp is in proper format
                if 'timestamp' in clean_record:
                    try:
                        datetime.fromisoformat(clean_record['timestamp'].replace('Z', '+00:00'))
                    except ValueError:
                        clean_record['timestamp'] = datetime.now().isoformat() + 'Z'
                
                # Add index action
                bulk_data.append({"index": {"_index": "logs"}})
                bulk_data.append(clean_record)
            
            if bulk_data:
                try:
                    response = es.bulk(body=bulk_data)
                    if response.get('errors'):
                        logger.warning(f"Some errors occurred in bulk insert")
                except Exception as e:
                    logger.error(f"Error in bulk insert: {str(e)}")
                    # Try individual inserts
                    for j in range(0, len(batch)):
                        try:
                            es.index(index="logs", body=batch[j])
                        except Exception as inner_e:
                            logger.error(f"Error indexing single record: {str(inner_e)}")
            
            imported += len(batch)
            logger.info(f"Elasticsearch: Imported {imported}/{total_records} records")
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "database": "Elasticsearch",
            "total_records": total_records,
            "duration_seconds": duration,
            "records_per_second": total_records / duration if duration > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error importing to Elasticsearch: {str(e)}")
        return {
            "database": "Elasticsearch",
            "error": str(e)
        }

def run_elasticsearch_queries(num_queries=20, query_types=None, log_levels=None):
    """Run query performance tests on Elasticsearch"""
    if query_types is None:
        query_types = ["level_filter", "time_range", "complex_query"]
    
    if log_levels is None:
        log_levels = ["INFO", "WARNING", "ERROR"]
    
    results = []
    
    try:
        # Connect to Elasticsearch
        logger.info("Connecting to Elasticsearch for queries...")
        es = Elasticsearch(["http://elasticsearch:9200"])
        
        # Check connection
        if not es.ping():
            logger.error("Cannot connect to Elasticsearch for queries! Please check if it's running.")
            return [{
                "database": "Elasticsearch",
                "error": "Failed to connect to Elasticsearch"
            }]
        
        logger.info("Elasticsearch connection successful for queries")
        
        # Check if index exists
        if not es.indices.exists(index="logs"):
            logger.error("Elasticsearch index 'logs' does not exist. Cannot run queries.")
            return [{
                "database": "Elasticsearch",
                "error": "Index 'logs' does not exist"
            }]
        
        logger.info("Running Elasticsearch queries...")
        # Run different types of queries
        for query_type in query_types:
            times = []
            
            for _ in range(num_queries):
                if query_type == "level_filter":
                    level = random.choice(log_levels)
                    start_time = time.time()
                    try:
                        es.search(index="logs", body={
                            "query": {
                                "term": {
                                    "level": level  # Use .keyword for exact matches
                                }
                            },
                            "size": 0  # Just count, don't return documents
                        })
                        times.append(time.time() - start_time)
                    except Exception as e:
                        logger.error(f"Elasticsearch level_filter query error: {e}")
                        
                elif query_type == "time_range":
                    hours = random.choice([1, 6, 24, 48])
                    threshold = datetime.now().timestamp() - (hours * 3600)
                    threshold_iso = datetime.fromtimestamp(threshold).isoformat() + 'Z'
                    
                    start_time = time.time()
                    try:
                        es.search(index="logs", body={
                            "query": {
                                "range": {
                                    "timestamp": {
                                        "gt": threshold_iso
                                    }
                                }
                            },
                            "size": 0
                        })
                        times.append(time.time() - start_time)
                    except Exception as e:
                        logger.error(f"Elasticsearch time_range query error: {e}")
                        
                elif query_type == "complex_query":
                    level = random.choice(log_levels)
                    hours = random.choice([1, 6, 24, 48])
                    threshold = datetime.now().timestamp() - (hours * 3600)
                    threshold_iso = datetime.fromtimestamp(threshold).isoformat() + 'Z'
                    
                    start_time = time.time()
                    try:
                        es.search(index="logs", body={
                            "query": {
                                "bool": {
                                    "must": [
                                        {"term": {"level": level}},
                                        {"range": {"timestamp": {"gt": threshold_iso}}},
                                        {"match": {"message": "test"}}
                                    ]
                                }
                            },
                            "size": 0
                        })
                        times.append(time.time() - start_time)
                    except Exception as e:
                        logger.error(f"Elasticsearch complex_query error: {e}")
            
            # Calculate average (only if we have times)
            if times:
                avg_time = sum(times) / len(times)
                results.append({
                    "database": "Elasticsearch",
                    "query_type": query_type,
                    "avg_duration_seconds": avg_time
                })
                logger.info(f"Elasticsearch {query_type} average time: {avg_time:.6f}s")
            else:
                logger.warning(f"No successful Elasticsearch queries for {query_type}")
                results.append({
                    "database": "Elasticsearch",
                    "query_type": query_type,
                    "error": "No successful queries"
                })
        
    except Exception as e:
        logger.error(f"Error running Elasticsearch queries: {str(e)}")
        results.append({
            "database": "Elasticsearch",
            "error": str(e)
        })
    
    return results

def run_query_tests(num_queries=20):
    """Run query performance tests on all databases"""
    results = []
    
    # Define test queries
    query_types = [
        "level_filter",
        "time_range",
        "complex_query"
    ]
    
    # Prepare test data
    log_levels = ["INFO", "WARNING", "ERROR"]
    
    # PostgreSQL queries
    try:
        conn = psycopg2.connect(
            host="postgres-db",  # Use the service name from docker-compose
            database="taskdb",
            user="devops",
            password="devops_password"
        )
        cursor = conn.cursor()
        
        logger.info("Running PostgreSQL queries...")
        # Run different types of queries
        for query_type in query_types:
            times = []
            
            for _ in range(num_queries):
                if query_type == "level_filter":
                    level = random.choice(log_levels)
                    start_time = time.time()
                    cursor.execute("SELECT COUNT(*) FROM logs WHERE level = %s", (level,))
                    cursor.fetchone()
                    times.append(time.time() - start_time)
                    
                elif query_type == "time_range":
                    hours = random.choice([1, 6, 24, 48])
                    start_time = time.time()
                    cursor.execute(
                        "SELECT COUNT(*) FROM logs WHERE timestamp > NOW() - INTERVAL '%s hours'", 
                        (hours,)
                    )
                    cursor.fetchone()
                    times.append(time.time() - start_time)
                    
                elif query_type == "complex_query":
                    level = random.choice(log_levels)
                    hours = random.choice([1, 6, 24, 48])
                    message_pattern = "%test%"
                    
                    start_time = time.time()
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM logs 
                        WHERE level = %s 
                        AND timestamp > NOW() - INTERVAL '%s hours'
                        AND message LIKE %s
                        """,
                        (level, hours, message_pattern)
                    )
                    cursor.fetchone()
                    times.append(time.time() - start_time)
            
            # Calculate average
            avg_time = sum(times) / len(times) if times else 0
            results.append({
                "database": "PostgreSQL",
                "query_type": query_type,
                "avg_duration_seconds": avg_time
            })
            logger.info(f"PostgreSQL {query_type} average time: {avg_time:.6f}s")
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error running PostgreSQL queries: {str(e)}")
        results.append({
            "database": "PostgreSQL",
            "error": str(e)
        })
    
    # MongoDB queries
    try:
        client = pymongo.MongoClient(
            "mongodb://devops:devops_password@mongodb:27017/admin"  # Use the service name
        )
        db = client.logs
        collection = db.app_logs
        
        logger.info("Running MongoDB queries...")
        # Run different types of queries
        for query_type in query_types:
            times = []
            
            for _ in range(num_queries):
                if query_type == "level_filter":
                    level = random.choice(log_levels)
                    start_time = time.time()
                    collection.count_documents({"level": level})
                    times.append(time.time() - start_time)
                    
                elif query_type == "time_range":
                    hours = random.choice([1, 6, 24, 48])
                    threshold = datetime.now().timestamp() - (hours * 3600)
                    threshold_iso = datetime.fromtimestamp(threshold).isoformat() + 'Z'
                    
                    start_time = time.time()
                    collection.count_documents({"timestamp": {"$gt": threshold_iso}})
                    times.append(time.time() - start_time)
                    
                elif query_type == "complex_query":
                    level = random.choice(log_levels)
                    hours = random.choice([1, 6, 24, 48])
                    threshold = datetime.now().timestamp() - (hours * 3600)
                    threshold_iso = datetime.fromtimestamp(threshold).isoformat() + 'Z'
                    
                    start_time = time.time()
                    collection.count_documents({
                        "level": level,
                        "timestamp": {"$gt": threshold_iso},
                        "message": {"$regex": "test"}
                    })
                    times.append(time.time() - start_time)
            
            # Calculate average
            avg_time = sum(times) / len(times) if times else 0
            results.append({
                "database": "MongoDB",
                "query_type": query_type,
                "avg_duration_seconds": avg_time
            })
            logger.info(f"MongoDB {query_type} average time: {avg_time:.6f}s")
        
        client.close()
    except Exception as e:
        logger.error(f"Error running MongoDB queries: {str(e)}")
        results.append({
            "database": "MongoDB",
            "error": str(e)
        })
    
    # Run Elasticsearch queries using the dedicated function
    es_results = run_elasticsearch_queries(num_queries, query_types, log_levels)
    results.extend(es_results)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Import logs to different databases and run performance tests')
    parser.add_argument('--file', help='Path to JSON log file (for backward compatibility)')
    parser.add_argument('--app-logs', help='Path pattern to application logs (e.g., logs/app.json)', default='')
    parser.add_argument('--text-logs', help='Path pattern to text logs (e.g., logs/app.log)', default='')
    parser.add_argument('--jenkins-logs', help='Path pattern to Jenkins logs (e.g., jenkins/*.log)', default='')
    parser.add_argument('--queries', type=int, default=20, help='Number of queries to run for testing')
    parser.add_argument('--skip-import', action='store_true', help='Skip import phase, run only queries')
    parser.add_argument('--import-only', action='store_true', help='Only import logs, skip query tests')
    args = parser.parse_args()
    
    all_results = {}
    
    if not args.skip_import:
        # Define log sources
        sources = []
        
        # Add generated logs if specified
        if args.file:
            sources.append({"type": "json", "path": args.file})
        
        # Add application logs if specified
        if args.app_logs:
            sources.append({"type": "json", "path": args.app_logs})
        
        # Add text logs if specified
        if args.text_logs:
            sources.append({"type": "text", "path": args.text_logs})
        
        # Add Jenkins logs if specified
        if args.jenkins_logs:
            sources.append({"type": "jenkins", "path": args.jenkins_logs})
        
        if not sources:
            logger.error("No log sources specified. Use --file, --app-logs, --text-logs, or --jenkins-logs")
            return
        
        # Collect logs from all sources
        records = collect_logs(sources)
        
        if not records:
            logger.error("No records found. Exiting.")
            return
        
        # Import to PostgreSQL
        logger.info("\nImporting to PostgreSQL...")
        pg_results = import_to_postgres(records)
        logger.info(f"PostgreSQL import completed in {pg_results.get('duration_seconds', 'N/A')} seconds")
        
        # Import to MongoDB
        logger.info("\nImporting to MongoDB...")
        mongo_results = import_to_mongodb(records)
        logger.info(f"MongoDB import completed in {mongo_results.get('duration_seconds', 'N/A')} seconds")
        
        # Import to Elasticsearch
        logger.info("\nImporting to Elasticsearch...")
        es_results = import_to_elasticsearch(records)
        logger.info(f"Elasticsearch import completed in {es_results.get('duration_seconds', 'N/A')} seconds")
        
        all_results["import_performance"] = [pg_results, mongo_results, es_results]
    else:
        logger.info("Skipping import phase as requested.")
    
    # Run query tests if not import-only
    if not args.import_only:
        logger.info("\nRunning query performance tests...")
        query_results = run_query_tests(args.queries)
        all_results["query_performance"] = query_results
    
    # Save results to file
    output_file = "performance_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"\nResults saved to {output_file}")
    
    # Print summary
    logger.info("\nPerformance Summary:")
    logger.info("====================")
    
    if "import_performance" in all_results:
        logger.info("\nImport Performance:")
        for result in all_results["import_performance"]:
            db = result.get("database")
            duration = result.get("duration_seconds", "N/A")
            rps = result.get("records_per_second", "N/A")
            
            # Handle the case where duration or rps might be strings
            if isinstance(duration, str) or isinstance(rps, str):
                logger.info(f"  {db}: {duration}s, {rps} records/s")
            else:
                logger.info(f"  {db}: {duration:.2f}s, {rps:.2f} records/s")
    
    if "query_performance" in all_results:
        logger.info("\nQuery Performance (Average in seconds):")
        for query_type in ["level_filter", "time_range", "complex_query"]:
            logger.info(f"\n  {query_type}:")
            for db in ["PostgreSQL", "MongoDB", "Elasticsearch"]:
                results = [r for r in all_results["query_performance"] if r.get("database") == db and r.get("query_type") == query_type]
                if results:
                    if "error" in results[0]:
                        logger.info(f"    {db}: ERROR - {results[0].get('error')}")
                    else:
                        avg_time = results[0].get("avg_duration_seconds", "N/A")
                        if isinstance(avg_time, str):
                            logger.info(f"    {db}: {avg_time}s")
                        else:
                            logger.info(f"    {db}: {avg_time:.6f}s")
                else:
                    logger.info(f"    {db}: No results")

if __name__ == "__main__":
    main()