pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'devops-task-app'
        DOCKER_TAG = "${env.BUILD_ID}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'python -m pytest app/tests/'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                docker-compose down || true
                docker-compose up -d
                '''
            }
        }
        
        stage('Integration Test') {
            steps {
                sh '''
                # Wait for application to start
                sleep 10
                
                # Run a simple integration test
                curl -s http://localhost:5000/health | grep "healthy" || exit 1
                
                # Create a task
                TASK_ID=$(curl -s -X POST -H "Content-Type: application/json" \
                    -d '{"title":"Test Task","description":"Created by Jenkins"}' \
                    http://localhost:5000/api/tasks | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
                
                # Verify task was created
                curl -s http://localhost:5000/api/tasks/${TASK_ID} | grep "Test Task" || exit 1
                
                echo "Integration tests passed!"
                '''
            }
        }
        
        stage('Log Collection') {
            steps {
                sh '''
                # Create a logs directory
                mkdir -p jenkins_logs
                
                # Collect logs from the application
                docker cp $(docker-compose ps -q app):/app/logs/app.log jenkins_logs/
                docker cp $(docker-compose ps -q app):/app/logs/app.json jenkins_logs/
                
                echo "Logs collected successfully!"
                '''
                
                // Archive logs as artifacts
                archiveArtifacts artifacts: 'jenkins_logs/**', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}