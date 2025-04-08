#!/bin/bash

echo "Setting up MongoDB for log storage..."

# Create logs collection in MongoDB
docker exec mongodb mongosh --username devops --password devops_password --authenticationDatabase admin --eval '
use logs;
db.createCollection("app_logs");
db.app_logs.createIndex({ "timestamp": 1 });
db.app_logs.createIndex({ "level": 1 });
db.app_logs.createIndex({ "request_id": 1 });
'

echo "MongoDB setup completed!"