# Project: product search by image and text
## Table of content
- [1. Overview](#overview)
  - [i. Introduction](#introduction)
  - [ii. Architecture](#architecture)
- [2. Local](#deploy-locally)
  - [i. Initial setup](#initial-setup)
  - [ii. Run application & monitoring services with Docker](#run-with-docker)
  - [iii. Run CI/CD pipeline](#cicd)
- [3. Cloud](#cloud)
  - [i. Deploy on GCP with k8s](#deploy-on-gcp)
  - [ii. CI/CD with Jenkins on cloud](#cicd-with-jenkins-on-cloud)


## Overview
### Introduction
This **Product Search** project aims at building a scalable system that can retrieve relevant items from a catalog using either images or text queries. Using `DeepFashion Product Images` dataset, it offer three basic use cases for e-commerce product search: upserting new products, searching by image, and searching by text. The solution is deployed on Cloud (GCP) & k8s with a CI/CD pipeline, and is monitored via observability services.

**Data Source:**
- [DeepFashion Product Images](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small?select=styles.csv)

### Architecture
**Overall Architecture:**
![System Architecture](./architecture.png)

**Technology Stack:**
- **Build application APIs**: FastAPI
- **ML Model**: CLIP model
- **Vector Database**: Pinecone for efficient vector search
- **Source control**: Git/Github
- **CI/CD pipeline**: A fully automated `Test -> Build -> Deploy` pipeline using Jenkins with PyTest.
- **Cloud**: Google Cloud Platform (GCP)
- **Container orchestration system**: Kubernetes (K8s)
- **K8s's package manager**: Helm
- **Observable tools**: Prometheus, Grafana, Jaeger, ELK (logs, traces, metrics)

## Local deployment
### Initial setup
Clone the repository:
```
git clone [https://github.com/thanhvu94/product-search-mlops.git](https://github.com/thanhvu94/product-search-mlops.git) product-search
cd product-search
```
### Run with Docker
Navigate to `src/` folder, then build and run the service on Docker:
```
cd src
docker compose up -d
```
Once everything is running, you can access all the UIs from your browser.
- FastAPI App: http://localhost:8000/docs
- Grafana (Metrics): http://localhost:3000 (Login: admin / admin)
- Jaeger (Traces): http://localhost:16686
- Prometheus: http://localhost:9090

### CI/CD
1. Navigate to `src/` folder, then build and run Jenkins:
```
cd src
docker compose -f docker-compose.jenkins.yml up -d
```
2. Install plugins: Docker, Docker Pipeline, Docker API, SSH Agent
3. Add credentials for the system in Jenkins Credentials manager:
  - `docker-creds` (for Docker Hub)
  - `prod-ssh-key` (for server deployment)
4. Configure the Jenkinsfile in your repository to point to your server's IP.
5. Create the "Pipeline" job in the Jenkins UI.
6. Click "Build Now"

## Cloud
### Initial setup
1. Open Google Cloud Console, choose `VM Instance` and create a new EC2 VM instance
- Machine type
- Disk
2. Setup SSH key to access to EC2 VM instance from your local machine
3. Setup allowed ports in Firewall
4. Remote access to EC2 VM instance
5. Install some libraries: docker, minikube ...

### Deploy on GCP
1. SSH to your VM on GCP
2. Clone the source code from git
```
git clone [https://github.com/thanhvu94/product-search-mlops.git](https://github.com/thanhvu94/product-search-mlops.git) product-search
cd product-search
```
3. Start minikube
```
minikube start --driver=docker --cpus=3 --memory=8192
```
4. Apply the k8s configuration to launch 3 pods
```
kubectl apply -f k8s/product-search.yaml
kubectl get pods
```
5. Install helm & create a  separate namespace for monitoring
```
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
kubectl create namespace monitoring
```
6. Add the Prometheus Community Repo
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword='admin'
```
7. Tell Prometheus to scrape metrics from product-search
```
kubectl label service product-search-service app=product-search
kubectl apply -f k8s/service-monitor.yaml
```
8. Enable port-forwarding for our services
```
kubectl port-forward svc/product-search-service 8000:80 --address 0.0.0.0
kubectl port-forward svc/prometheus-stack-grafana 3000:80 -n monitoring
kubectl port-forward --address 0.0.0.0 -n monitoring svc/prometheus-stack-kube-prom-prometheus 9090:9090
```
9. Open Prometheus & Grafana
- FastAPI App: http://<VM_EXTERNAL_IP>:8000/docs
- Grafana (Metrics): http://<VM_EXTERNAL_IP>:3000 (Login: admin / admin)
- Prometheus: http://<VM_EXTERNAL_IP>:9090

### CI/CD with Jenkins on cloud
1. Inside VM, navigate to `product-search/` folder, then build and run Jenkins:
```
cd src
docker-compose -f docker-compose.jenkins.yml up -d
```
2. Now we can access Jenkins via http://<VM_EXTERNAL_IP>:8080
3. Install plugins
4. Set up credentials
5. Configure the Jenkinsfile in your repository to point to your server's IP.
6. Create the "Pipeline" job in the Jenkins UI.
7. Click "Build Now"