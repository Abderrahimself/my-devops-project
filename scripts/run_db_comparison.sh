# #!/bin/bash

# # Check if docker is running
# if ! docker ps &> /dev/null; then
#     echo "Docker is not running! Please start Docker first."
#     exit 1
# fi

# # Make sure all containers are up
# echo "Making sure all services are running..."
# cd $(dirname $0)/..
# docker-compose up -d

# # Setup all databases
# echo -e "\n======= Setting up databases ======="
# ./scripts/db_scripts/setup_postgres.sh
# ./scripts/db_scripts/setup_mongodb.sh
# ./scripts/db_scripts/setup_elasticsearch.sh

# # Generate test logs
# echo -e "\n======= Generating test logs ======="
# python3 ./scripts/generate_test_logs.py --count 10000 --output ./logs/test_logs.json

# # Install required Python packages
# echo -e "\n======= Installing required packages ======="
# pip3 install psycopg2-binary pymongo elasticsearch matplotlib numpy

# # Run the comparison
# echo -e "\n======= Running performance comparison ======="
# python3 ./scripts/import_logs.py --file ./logs/test_logs.json --queries 20

# # Create visualization
# echo -e "\n======= Creating visualization ======="
# python3 ./scripts/visualize_results.py --results performance_results.json --output ./reports

# echo -e "\n======= Database Comparison Completed ======="
# echo "Results are saved to performance_results.json"
# echo "Visualizations and report are available in the reports directory"
# echo "Open ./reports/performance_report.html to view the complete report"
# echo ""
# echo "You can view the logs in:"
# echo "  - PostgreSQL: Connect to the database and query the 'logs' table"
# echo "  - MongoDB: Use MongoDB Compass or mongo shell to view 'logs.app_logs' collection"
# echo "  - Elasticsearch: Open Kibana at http://localhost:5601 to view logs"


#!/bin/bash

# Check if docker is running
if ! docker ps &> /dev/null; then
    echo "Docker is not running! Please start Docker first."
    exit 1
fi

# Set a timeout for waiting for services
TIMEOUT=60
START_TIME=$(date +%s)

# Make sure all containers are up
echo "Making sure all services are running..."
cd $(dirname $0)/..
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "Timeout waiting for services to be ready. Continuing anyway..."
        break
    fi
    
    if docker ps | grep -q "postgres" && \
       docker ps | grep -q "mongodb" && \
       docker ps | grep -q "elasticsearch"; then
        echo "All services are running!"
        break
    fi
    
    echo "Waiting for services to be ready... ($ELAPSED seconds elapsed)"
    sleep 5
done

# Setup all databases
echo -e "\n======= Setting up databases ======="
./scripts/db_scripts/setup_postgres.sh
./scripts/db_scripts/setup_mongodb.sh
./scripts/db_scripts/setup_elasticsearch.sh

# Generate test logs
echo -e "\n======= Generating test logs ======="
mkdir -p logs
chmod 777 logs
python3 ./scripts/generate_test_logs.py --count 5000 --output ./logs/test_logs.json

# Install required Python packages
echo -e "\n======= Installing required packages ======="
pip3 install psycopg2-binary pymongo elasticsearch matplotlib numpy

# Run the comparison
echo -e "\n======= Running performance comparison ======="
python3 ./scripts/import_logs.py --file ./logs/test_logs.json --queries 10

# Create visualization
echo -e "\n======= Creating visualization ======="
mkdir -p reports
chmod 777 reports
python3 ./scripts/visualize_results.py --results performance_results.json --output ./reports

echo -e "\n======= Database Comparison Completed ======="
echo "Results are saved to performance_results.json"
echo "Visualizations and report are available in the reports directory"
echo "Open ./reports/performance_report.html to view the complete report"
echo ""
echo "You can view the logs in:"
echo "  - PostgreSQL: Connect to the database and query the 'logs' table"
echo "  - MongoDB: Use MongoDB Compass or mongo shell to view 'logs.app_logs' collection"
echo "  - Elasticsearch: Open Kibana at http://localhost:5601 to view logs"