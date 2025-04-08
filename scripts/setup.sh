#!/bin/bash

# Create necessary directories
mkdir -p logs

# Check if databases should be set up
if [ "$1" == "--with-db-comparison" ]; then
    # Build and start all containers
    docker-compose up -d
    
    # Set up databases for comparison
    ./scripts/db_scripts/setup_postgres.sh
    ./scripts/db_scripts/setup_mongodb.sh
    ./scripts/db_scripts/setup_elasticsearch.sh
    
    echo "Application and all databases are running!"
    echo "  - Application: http://localhost:5000"
    echo "  - Kibana: http://localhost:5601"
    
    echo "To run the database comparison: ./scripts/run_db_comparison.sh"
else
    # Build and start only app and postgres
    docker-compose up -d app postgres
    
    echo "Application is running at http://localhost:5000"
fi

echo "API endpoints:"
echo "  GET    /health                - Health check"
echo "  GET    /api/tasks             - Get all tasks"
echo "  GET    /api/tasks/{task_id}   - Get a specific task"
echo "  POST   /api/tasks             - Create a new task"
echo "  PUT    /api/tasks/{task_id}   - Update a task"
echo "  DELETE /api/tasks/{task_id}   - Delete a task"
echo "  POST   /api/generate-logs     - Generate test logs"

echo "To view logs: docker-compose logs -f app"