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

def read_log_file(file_path):
    """Read log records from JSON log file"""
    records = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    records.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        return records
    except Exception as e:
        print(f"Error reading log file: {str(e)}")
        return []

def import_to_postgres(records, batch_size=100):
    """Import log records to PostgreSQL"""
    try:
        # conn = psycopg2.connect(
        #     host="localhost",
        #     database="taskdb",
        #     user="devops",
        #     password="devops_password"
        # )

        conn = psycopg2.connect(
            host="postgres-db",  # Use the service name from docker-compose
            database="taskdb",
            user="devops",
            password="devops_password"
        )
        cursor = conn.cursor()
        
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
                        datetime.fromisoformat(record.get('timestamp')),
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
            print(f"PostgreSQL: Imported {imported}/{total_records} records")
        
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
        print(f"Error importing to PostgreSQL: {str(e)}")
        return {
            "database": "PostgreSQL",
            "error": str(e)
        }

def import_to_mongodb(records, batch_size=100):
    """Import log records to MongoDB"""
    try:
        # client = pymongo.MongoClient(
        #     "mongodb://devops:devops_password@localhost:27017/admin"
        # )

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
            print(f"MongoDB: Imported {min(i+batch_size, total_records)}/{total_records} records")
        
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
        print(f"Error importing to MongoDB: {str(e)}")
        return {
            "database": "MongoDB",
            "error": str(e)
        }

def import_to_elasticsearch(records, batch_size=100):
    """Import log records to Elasticsearch"""
    # try:
    #     from elasticsearch import Elasticsearch
        
    #     # Connect to Elasticsearch
    #     print("Connecting to Elasticsearch...")
    #     # es = Elasticsearch(["http://localhost:9200"])
    #     es = Elasticsearch(["http://elasticsearch:9200"])  # Use the service name        
    #     # Check connection
    #     if not es.ping():
    #         print("Cannot connect to Elasticsearch! Please check if it's running.")
    #         return {
    #             "database": "Elasticsearch",
    #             "error": "Failed to connect to Elasticsearch"
    #         }
        
    #     print(f"Elasticsearch connection successful")
        
    #     start_time = time.time()
    #     total_records = len(records)
    #     imported = 0
        
    #     # Bulk insert
    #     for i in range(0, total_records, batch_size):
    #         batch = records[i:i+batch_size]
    #         bulk_data = []
            
    #         for record in batch:
    #             # Clean any problematic fields for ES
    #             clean_record = record.copy()
    #             # Ensure timestamp is in proper format
    #             if 'timestamp' in clean_record:
    #                 try:
    #                     datetime.fromisoformat(clean_record['timestamp'])
    #                 except ValueError:
    #                     clean_record['timestamp'] = datetime.now().isoformat()
                
    #             # Add index action
    #             bulk_data.append({"index": {"_index": "logs"}})
    #             bulk_data.append(clean_record)
            
    #         if bulk_data:
    #             try:
    #                 response = es.bulk(body=bulk_data)
    #                 if response.get('errors'):
    #                     print(f"Some errors occurred in bulk insert")
    #             except Exception as e:
    #                 print(f"Error in bulk insert: {str(e)}")
    #                 # Try individual inserts
    #                 for j in range(0, len(batch)):
    #                     try:
    #                         es.index(index="logs", body=batch[j])
    #                     except Exception as inner_e:
    #                         print(f"Error indexing single record: {str(inner_e)}")
            
    #         imported += len(batch)
    #         print(f"Elasticsearch: Imported {imported}/{total_records} records")
        
    #     end_time = time.time()
    #     duration = end_time - start_time
        
    #     return {
    #         "database": "Elasticsearch",
    #         "total_records": total_records,
    #         "duration_seconds": duration,
    #         "records_per_second": total_records / duration if duration > 0 else 0
    #     }
    # except Exception as e:
    #     print(f"Error importing to Elasticsearch: {str(e)}")
    #     return {
    #         "database": "Elasticsearch",
    #         "error": str(e)
    #     }

    # Elasticsearch queries
    try:
        es = Elasticsearch(["http://elasticsearch:9200"])
        
        # Check connection and index existence
        if not es.indices.exists(index="logs"):
            print("Elasticsearch index 'logs' does not exist. Creating it...")
            es.indices.create(index="logs")
        
        print("Running Elasticsearch queries...")
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
                                    "level": level
                                }
                            },
                            "size": 0  # Just count, don't return documents
                        })
                        times.append(time.time() - start_time)
                    except Exception as e:
                        print(f"Elasticsearch level_filter query error: {e}")
                        
                elif query_type == "time_range":
                    hours = random.choice([1, 6, 24, 48])
                    threshold = datetime.now().timestamp() - (hours * 3600)
                    threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
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
                        print(f"Elasticsearch time_range query error: {e}")
                        
                elif query_type == "complex_query":
                    level = random.choice(log_levels)
                    hours = random.choice([1, 6, 24, 48])
                    threshold = datetime.now().timestamp() - (hours * 3600)
                    threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
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
                        print(f"Elasticsearch complex_query error: {e}")
            
            # Calculate average (only if we have times)
            if times:
                avg_time = sum(times) / len(times)
                results.append({
                    "database": "Elasticsearch",
                    "query_type": query_type,
                    "avg_duration_seconds": avg_time
                })
                print(f"Elasticsearch {query_type} average time: {avg_time:.6f}s")
            else:
                print(f"No successful Elasticsearch queries for {query_type}")
        
    except Exception as e:
        print(f"Error running Elasticsearch queries: {str(e)}")
        results.append({
            "database": "Elasticsearch",
            "error": str(e)
        })

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
    time_periods = [
        {"hours": 1},
        {"hours": 24},
        {"days": 7}
    ]
    
    # PostgreSQL queries
    try:
        # conn = psycopg2.connect(
        #     host="localhost",
        #     database="taskdb",
        #     user="devops",
        #     password="devops_password"
        # )

        conn = psycopg2.connect(
            host="postgres-db",  # Use the service name from docker-compose
            database="taskdb",
            user="devops",
            password="devops_password"
        )
        cursor = conn.cursor()
        
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
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error running PostgreSQL queries: {str(e)}")
        results.append({
            "database": "PostgreSQL",
            "error": str(e)
        })
    
    # MongoDB queries
    try:
        # client = pymongo.MongoClient(
        #     "mongodb://devops:devops_password@localhost:27017/admin"
        # )

        client = pymongo.MongoClient(
            "mongodb://devops:devops_password@mongodb:27017/admin"  # Use the service name
        )
        db = client.logs
        collection = db.app_logs
        
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
                    threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
                    start_time = time.time()
                    collection.count_documents({"timestamp": {"$gt": threshold_iso}})
                    times.append(time.time() - start_time)
                    
                elif query_type == "complex_query":
                    level = random.choice(log_levels)
                    hours = random.choice([1, 6, 24, 48])
                    threshold = datetime.now().timestamp() - (hours * 3600)
                    threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                    
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
        
        client.close()
    except Exception as e:
        print(f"Error running MongoDB queries: {str(e)}")
        results.append({
            "database": "MongoDB",
            "error": str(e)
        })
    
    # Elasticsearch queries
    try:
        from elasticsearch import Elasticsearch
        # es = Elasticsearch(["http://localhost:9200"])
        es = Elasticsearch(["http://elasticsearch:9200"])  # Use the service name        
        # Check connection
        if not es.ping():
            print("Cannot connect to Elasticsearch for queries! Please check if it's running.")
            results.append({
                "database": "Elasticsearch",
                "error": "Failed to connect to Elasticsearch"
            })
        else:
            # Run different types of queries
            for query_type in query_types:
                times = []
                
                for _ in range(num_queries):
                    if query_type == "level_filter":
                        level = random.choice(log_levels)
                        start_time = time.time()
                        es.count(index="logs", body={"query": {"term": {"level": level}}})
                        times.append(time.time() - start_time)
                        
                    elif query_type == "time_range":
                        hours = random.choice([1, 6, 24, 48])
                        threshold = datetime.now().timestamp() - (hours * 3600)
                        threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                        
                        start_time = time.time()
                        es.count(index="logs", body={
                            "query": {
                                "range": {
                                    "timestamp": {
                                        "gt": threshold_iso
                                    }
                                }
                            }
                        })
                        times.append(time.time() - start_time)
                        
                    elif query_type == "complex_query":
                        level = random.choice(log_levels)
                        hours = random.choice([1, 6, 24, 48])
                        threshold = datetime.now().timestamp() - (hours * 3600)
                        threshold_iso = datetime.fromtimestamp(threshold).isoformat()
                        
                        start_time = time.time()
                        es.count(index="logs", body={
                            "query": {
                                "bool": {
                                    "must": [
                                        {"term": {"level": level}},
                                        {"range": {"timestamp": {"gt": threshold_iso}}},
                                        {"match": {"message": "test"}}
                                    ]
                                }
                            }
                        })
                        times.append(time.time() - start_time)
                
                # Calculate average
                avg_time = sum(times) / len(times) if times else 0
                results.append({
                    "database": "Elasticsearch",
                    "query_type": query_type,
                    "avg_duration_seconds": avg_time
                })
    except Exception as e:
        print(f"Error running Elasticsearch queries: {str(e)}")
        results.append({
            "database": "Elasticsearch",
            "error": str(e)
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Import logs to different databases and run performance tests')
    parser.add_argument('--file', required=True, help='Path to JSON log file')
    parser.add_argument('--queries', type=int, default=20, help='Number of queries to run for testing')
    args = parser.parse_args()
    
    # Read log records
    print(f"Reading log records from {args.file}...")
    records = read_log_file(args.file)
    if not records:
        print("No records found. Exiting.")
        return
    print(f"Read {len(records)} log records.")
    
    # Import to PostgreSQL
    print("\nImporting to PostgreSQL...")
    pg_results = import_to_postgres(records)
    print(f"PostgreSQL import completed in {pg_results.get('duration_seconds', 'N/A')} seconds")
    
    # Import to MongoDB
    print("\nImporting to MongoDB...")
    mongo_results = import_to_mongodb(records)
    print(f"MongoDB import completed in {mongo_results.get('duration_seconds', 'N/A')} seconds")
    
    # Import to Elasticsearch
    print("\nImporting to Elasticsearch...")
    es_results = import_to_elasticsearch(records)
    print(f"Elasticsearch import completed in {es_results.get('duration_seconds', 'N/A')} seconds")
    
    # Run query tests
    print("\nRunning query performance tests...")
    query_results = run_query_tests(args.queries)
    
    # Combine results
    all_results = {
        "import_performance": [pg_results, mongo_results, es_results],
        "query_performance": query_results
    }
    
    # Save results to file
    output_file = "performance_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Print summary
    print("\nPerformance Summary:")
    print("====================")
    print("\nImport Performance:")
    for result in [pg_results, mongo_results, es_results]:
        db = result.get("database")
        duration = result.get("duration_seconds", "N/A")
        rps = result.get("records_per_second", "N/A")
        
        # Handle the case where duration or rps might be strings
        if isinstance(duration, str) or isinstance(rps, str):
            print(f"  {db}: {duration}s, {rps} records/s")
        else:
            print(f"  {db}: {duration:.2f}s, {rps:.2f} records/s")
    
    print("\nQuery Performance (Average in seconds):")
    for query_type in ["level_filter", "time_range", "complex_query"]:
        print(f"\n  {query_type}:")
        for db in ["PostgreSQL", "MongoDB", "Elasticsearch"]:
            results = [r for r in query_results if r.get("database") == db and r.get("query_type") == query_type]
            if results:
                avg_time = results[0].get("avg_duration_seconds", "N/A")
                if isinstance(avg_time, str):
                    print(f"    {db}: {avg_time}s")
                else:
                    print(f"    {db}: {avg_time:.6f}s")

if __name__ == "__main__":
    main()