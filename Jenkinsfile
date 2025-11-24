pipeline {
    // Run this pipeline on any agent
    agent any

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Display timestamp at each job in the pipeline
        timestamps()
    }

    // Environment variables
    environment {
        // Docker
        DOCKER_HUB_USER         = "vunt94"
        IMAGE_NAME              = "product-search-app"
        DOCKER_CREDENTIAL_ID    = "docker-creds"
        
        // SSH credential on EC2 VM (GCP)
        SSH_CREDENTIAL_ID       = "prod-ssh-key"
        PROD_SERVER_USER        = "vunguyen" 
        PROD_SERVER_IP          = "136.112.134.188"  // Public IP of EC2 VM
        PROD_COMPOSE_PATH       = "/home/vunguyen/product-search"

        // Run Jenkins with same version as Docker
        DOCKER_API_VERSION      = "1.41"
    }

    stages {
        stage('Test') {
            agent {
                docker {
                    image 'python:3.11' 
                }
            }
            steps {
                echo 'Testing model correctness...'
                // Install requirements and run PyTest
                sh 'pip install --timeout=600 -r requirements.txt && pytest'
            }
        }

        stage('Build') {
            steps {
                script {
                    echo "Building image for deployment..."
                    // Build application image (tag build number)
                    def dockerImage = docker.build("${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    
                    echo "Pushing image to dockerhub..."
                    // Log in to Docker Hub using our credential ID & push image with latest tag
                    docker.withRegistry("https://registry.hub.docker.com", env.DOCKER_CREDENTIAL_ID) {
                        dockerImage.push()
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying new image to server..."
                // Login to EC2 VM
                sshagent([env.SSH_CREDENTIAL_ID]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${env.PROD_SERVER_USER}@${env.PROD_SERVER_IP} '''
                            echo "Logged in to production server!"
                            
                            # Navigate to the docker-compose project directory
                            cd ${env.PROD_COMPOSE_PATH}
                            
                            # 1. Pull the new image (tagged 'latest')
                            echo "Pulling new image: ${env.DOCKER_HUB_USER}/${env.IMAGE_NAME}:latest"
                            docker-compose pull product-search-app
                            
                            # 2. Restart the app container only
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