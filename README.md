# DevOps Logs Persistence - Performance Comparison

This project demonstrates a practical implementation for comparing different database technologies (PostgreSQL, MongoDB, and Elasticsearch) for storing and analyzing DevOps logs. It includes a Flask-based task manager application, a comprehensive logging system, and tools for performance analysis.

## Project Overview

This application serves as a practical example for the research topic:
"Optimization of DevOps Log Persistence in NoSQL Databases: Comparative Approach and Technical Implementation"

The project includes:
1. A Flask task manager RESTful API with PostgreSQL backend
2. Custom logging system that stores logs in multiple databases
3. Performance analysis tools that compare PostgreSQL, MongoDB, and Elasticsearch
4. CI/CD pipeline with Jenkins
5. Docker containerization for all components


## Requirements

- Docker and Docker Compose
- Python 3.9+
- Jenkins (for CI/CD)

## Installation and Setup

### Using Docker Compose (Recommended)

The easiest way to run the complete environment is using Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/Abderrahimself/my-devops-project.git
   cd my-devops-project
   ```
   

2. Start the complete environment:
   ```bash
   docker-compose up -d
   ```
   

   This will start:
   - PostgreSQL database
   - MongoDB database
   - Elasticsearch service
   - Task Manager application
   - Jenkins for CI/CD

3. Access the services:
   - Task Manager API: http://localhost:5000
   - Jenkins: http://localhost:8080
   - Performance Dashboard: http://localhost:8050 (after running analysis)

## Database Comparison

The project compares three database technologies for log storage:

1. PostgreSQL: Traditional relational database with JSONB support
2. MongoDB: Document-oriented NoSQL database
3. Elasticsearch: Distributed search and analytics engine

The comparison includes:
- Insertion performance (single and bulk)
- Query performance
- CPU and RAM usage

## API Documentation

### Task Endpoints

- GET /tasks - List all tasks
- POST /tasks - Create a new task 
  json
  {
    "title": "Task title", 
    "description": "Task description", 
    "status": "pending"
  }
  
- GET /tasks/{id} - Get a specific task
- PUT /tasks/{id} - Update a task
- DELETE /tasks/{id} - Delete a task

## CI/CD Pipeline with Jenkins

The project includes a Jenkinsfile that defines a complete CI/CD pipeline:

1. Build: Builds and tests the application
2. Test: Runs unit tests
3. Deploy: Deploys the application using Docker
4. Performance Analysis: Generates load and analyzes performance

To set up the Jenkins pipeline:

1. Access Jenkins at http://localhost:8080
2. Create a new Pipeline job
3. Configure it to use Pipeline script from SCM
4. Set the Repository URL to your project repository
5. Set the Script Path to "Jenkinsfile"

## Troubleshooting

Connection Issues
- Ensure all containers are running: docker-compose ps

Database Setup Issues
- Manually run the setup scripts: ./scripts/db_scripts/setup_postgres.sh


Jenkins Pipeline Failures
- Check Jenkins logs for specific error messages
- Ensure environment variables are properly set
- Verify Docker commands are compatible with your environment

## License

MIT

## Contributors

- Mossab Arektout
- Abderrahim Mabrouk
- Saad Moussaid
- Marouane Es-sdiki
