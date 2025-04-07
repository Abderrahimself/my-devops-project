#!/bin/bash

# Create a docker-compose file for Jenkins
cat > jenkins-docker-compose.yml << EOF
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins-data:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
    networks:
      - jenkins-network

networks:
  jenkins-network:
    driver: bridge

volumes:
  jenkins-data:
EOF

# Start Jenkins
docker-compose -f jenkins-docker-compose.yml up -d

# Wait for Jenkins to start
echo "Waiting for Jenkins to start..."
sleep 30

# Get the initial admin password
JENKINS_CONTAINER_ID=$(docker ps -q --filter "name=jenkins")
JENKINS_ADMIN_PASSWORD=$(docker exec $JENKINS_CONTAINER_ID cat /var/jenkins_home/secrets/initialAdminPassword)

echo "Jenkins is running at http://localhost:8080"
echo "Initial admin password: $JENKINS_ADMIN_PASSWORD"

# Install Docker inside Jenkins
docker exec $JENKINS_CONTAINER_ID apt-get update -y
docker exec $JENKINS_CONTAINER_ID apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
docker exec $JENKINS_CONTAINER_ID curl -fsSL https://download.docker.com/linux/debian/gpg | docker exec -i $JENKINS_CONTAINER_ID apt-key add -
docker exec $JENKINS_CONTAINER_ID echo "deb [arch=amd64] https://download.docker.com/linux/debian $(docker exec $JENKINS_CONTAINER_ID lsb_release -cs) stable" | docker exec -i $JENKINS_CONTAINER_ID tee /etc/apt/sources.list.d/docker.list > /dev/null
docker exec $JENKINS_CONTAINER_ID apt-get update -y
docker exec $JENKINS_CONTAINER_ID apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose inside Jenkins
docker exec $JENKINS_CONTAINER_ID curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
docker exec $JENKINS_CONTAINER_ID chmod +x /usr/local/bin/docker-compose

# Install Python and pip inside Jenkins
docker exec $JENKINS_CONTAINER_ID apt-get install -y python3 python3-pip
docker exec $JENKINS_CONTAINER_ID pip3 install pytest requests pytest-cov

echo "Jenkins setup completed!"
echo "Next steps:"
echo "1. Go to http://localhost:8080 and log in with the admin password above"
echo "2. Install suggested plugins"
echo "3. Create an admin user"
echo "4. Install additional plugins: Docker, Docker Pipeline, Pipeline Utility Steps"
echo "5. Create a new Pipeline job using the Jenkinsfile in your project"