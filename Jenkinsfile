// This file MUST be at the root of your Git repository.

pipeline {
    // Run this pipeline on any agent
    agent any

    // --- (USER) EDIT THESE VARIABLES ---
    // These environment variables are used in the pipeline stages.
    // Make sure they match your setup.
    environment {
        // Your Docker Hub info (same as before)
        DOCKER_HUB_USER         = "vunt94"
        IMAGE_NAME              = "product-search-app"
        DOCKER_CREDENTIAL_ID    = "docker-creds"
        
        // --- (USER) EDIT THESE ---
        // Credentials ID for SSH Key (same as before)
        SSH_CREDENTIAL_ID       = "prod-ssh-key"
        
        // Your username on the EC2 VM
        PROD_SERVER_USER        = "ubuntu" 
        
        // Jenkins is SSH-ing to its own host VM
        PROD_SERVER_IP          = "127.0.0.1" 
        
        // The *absolute path* where you cloned your repo on the EC2 VM
        PROD_COMPOSE_PATH       = "/home/ubuntu/product-search-stack"
    }

    stages {
        // ---------------------------------
        // CI (Continuous Integration)
        // ---------------------------------

        stage('Checkout') {
            steps {
                // Get the code from Git
                echo 'Checking out code...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                // Build the product-search-app image using the Dockerfile
                echo "Building image: ${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
                script {
                    docker.build("${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                }
            }
        }

        stage('Run Tests') {
            steps {
                // --- PLACEHOLDER ---
                // This is where you would run tests (e.g., pytest)
                // Example: docker.image(...).inside { sh 'pytest' }
                echo "Running tests... (placeholder)"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                // Log in to Docker Hub and push the new image
                echo "Pushing image to Docker Hub..."
                script {
                    // Use the 'docker-creds' credentials from Jenkins
                    docker.withRegistry("https://registry.hub.docker.com", env.DOCKER_CREDENTIAL_ID) {
                        
                        // Push the build-number-tagged image
                        docker.image("${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}").push()
                        
                        // Also tag this build as 'latest' and push it
                        docker.image("${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}").push("latest")
                    }
                }
            }
        }

        // ---------------------------------
        // CD (Continuous Deployment)
        // ---------------------------------

        stage('Deploy to Production') {
            steps {
                // Use the 'prod-ssh-key' credentials to log in to your server
                sshagent([env.SSH_CREDENTIAL_ID]) {
                    
                    // SSH into the server and run the deployment commands
                    sh """
                        ssh -o StrictHostKeyChecking=no ${env.PROD_SERVER_USER}@${env.PROD_SERVER_IP} '''
                            echo "Logged in to production server!"
                            
                            # Navigate to the docker-compose project directory
                            cd ${env.PROD_COMPOSE_PATH}
                            
                            # 1. Pull the new image (tagged 'latest')
                            echo "Pulling new image: ${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:latest"
                            docker-compose pull product-search-app
                            
                            # 2. Restart *only* the app container
                            # --no-deps stops docker-compose from touching other running services
                            echo "Restarting product-search-app container..."
                            docker-compose up -d --no-deps product-search-app
                            
                            echo "Deployment complete!"
                        '''
                    """
                }
            }
        }
    }

    // ---------------------------------
    // POST-BUILD ACTIONS
    // ---------------------------------
    post {
        always {
            // Clean up the built image from the Jenkins server to save space
            script {
                sh "docker rmi ${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
                sh "docker rmi ${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:latest"
            }
            echo 'Cleanup complete.'
        }
    }
}