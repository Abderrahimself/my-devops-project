#!/bin/bash

echo "Setting up Elasticsearch for log storage..."

# Wait for Elasticsearch to be ready
while ! curl -s http://localhost:9200 > /dev/null; do
    echo "Waiting for Elasticsearch to be ready..."
    sleep 5
done

# Create logs index in Elasticsearch
curl -X PUT "localhost:9200/logs" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "timestamp": {
        "type": "date"
      },
      "level": {
        "type": "keyword"
      },
      "message": {
        "type": "text"
      },
      "module": {
        "type": "keyword"
      },
      "function": {
        "type": "keyword"
      },
      "line": {
        "type": "integer"
      },
      "request_id": {
        "type": "keyword"
      },
      "user_agent": {
        "type": "text"
      },
      "ip": {
        "type": "ip"
      }
    }
  }
}
'

# Create a Kibana index pattern
sleep 5  # Wait for index to be ready
curl -X POST "localhost:5601/api/saved_objects/index-pattern/logs" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' -d'
{
  "attributes": {
    "title": "logs*",
    "timeFieldName": "timestamp"
  }
}
'

echo "Elasticsearch setup completed!"