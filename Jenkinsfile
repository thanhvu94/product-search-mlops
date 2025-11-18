// This file MUST be at the root of your Git repository.
pipeline {
    // Run this pipeline on any agent
    agent any

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    // --- (USER) EDIT THESE VARIABLES ---
    // These environment variables are used in the pipeline stages.
    // Make sure they match your setup.
    environment {
        // Your Docker Hub info (same as before)
        DOCKER_HUB_USER         = "vunt94"
        IMAGE_NAME              = "product-search-app"
        // Credentials
        DOCKER_CREDENTIAL_ID    = "docker-creds"
        
        // --- (USER) EDIT THESE ---
        // Credentials ID for SSH Key (same as before)
        SSH_CREDENTIAL_ID       = "prod-ssh-key"
        
        // Your username on the EC2 VM
        PROD_SERVER_USER        = "ubuntu" 
        
        // Jenkins is SSH-ing to its own host VM
        PROD_SERVER_IP          = "54.206.93.56" 
        
        // The *absolute path* where you cloned your repo on the EC2 VM
        PROD_COMPOSE_PATH       = "/home/ubuntu/product-search-stack"
    }

    stages {
        // ---------------------------------
        // CI - Test
        // ---------------------------------
        stage('Test') {
            agent {
                // Use a Python 3.11 image to match our Dockerfile
                docker {
                    image 'python:3.11' 
                }
            }
            steps {
                echo 'Testing model correctness...'
                // Install all requirements and run pytest
                // We add --timeout=600 for the pip install, just in case
                sh 'pip install --timeout=600 -r requirements.txt && pytest'
            }
        }

        // ---------------------------------
        // CI - Build & Push
        // ---------------------------------
        stage('Build') {
            steps {
                script {
                    echo "Building image for deployment..."
                    // Build the image and tag it with the build number
                    // This uses the Docker Pipeline plugin, not the 'docker' command
                    def dockerImage = docker.build("${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    
                    echo "Pushing image to dockerhub..."
                    // Log in to Docker Hub using our credential ID
                    docker.withRegistry("https://registry.hub.docker.com", env.DOCKER_CREDENTIAL_ID) {
                        // Push the build-number-tagged image
                        dockerImage.push()
                        
                        // Also tag this build as 'latest' and push it
                        dockerImage.push("latest")
                    }
                }
            }
        }

        // ---------------------------------
        // CD - Deploy
        // ---------------------------------
        stage('Deploy') {
            steps {
                echo "Deploying new image to server..."
                // Use the 'prod-ssh-key' credentials to log in to our server
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
}