# #!/bin/bash

# echo "Setting up MongoDB for log storage..."

# # Create logs collection in MongoDB
# docker exec mongodb mongosh --username devops --password devops_password --authenticationDatabase admin --eval '
# use logs;
# db.createCollection("app_logs");
# db.app_logs.createIndex({ "timestamp": 1 });
# db.app_logs.createIndex({ "level": 1 });
# db.app_logs.createIndex({ "request_id": 1 });
# '

# echo "MongoDB setup completed!"

#!/bin/bash

echo "Setting up MongoDB for log storage..."

# Get the container ID of the mongodb container
MONGODB_CONTAINER=$(docker ps --filter "name=mongodb" -q | head -n 1)

if [ -z "$MONGODB_CONTAINER" ]; then
    echo "Error: MongoDB container not found. Skipping setup."
    exit 0
fi

# Create logs collection in MongoDB
docker exec $MONGODB_CONTAINER mongosh --username devops --password devops_password --authenticationDatabase admin --eval '
use logs;
db.createCollection("app_logs");
db.app_logs.createIndex({ "timestamp": 1 });
db.app_logs.createIndex({ "level": 1 });
db.app_logs.createIndex({ "request_id": 1 });
'

echo "MongoDB setup completed!"