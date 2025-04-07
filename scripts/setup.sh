#!/bin/bash

# Create necessary directories
mkdir -p logs

# Build and start the containers
docker-compose up -d

echo "Application is running at http://localhost:5000"
echo "API endpoints:"
echo "  GET    /health                - Health check"
echo "  GET    /api/tasks             - Get all tasks"
echo "  GET    /api/tasks/{task_id}   - Get a specific task"
echo "  POST   /api/tasks             - Create a new task"
echo "  PUT    /api/tasks/{task_id}   - Update a task"
echo "  DELETE /api/tasks/{task_id}   - Delete a task"

echo "To view logs: docker-compose logs -f app"