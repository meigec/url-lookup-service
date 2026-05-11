# DevOps Guide: CI/CD Pipeline with Self-Hosted Runner

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [One-Time Environment Setup](#one-time-environment-setup)
3. [Self-Hosted Runner Configuration](#self-hosted-runner-configuration)
4. [CI/CD Pipeline Overview](#cicd-pipeline-overview)
5. [Deployment Commands](#deployment-commands)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Software | Version | Installation |
|----------|---------|--------------|
| Docker Desktop | Latest | `brew install --cask docker` |
| Minikube | v1.28+ | `brew install minikube` |
| kubectl | v1.28+ | `brew install kubectl` |
| GitHub CLI | Latest | `brew install gh` |

---

## One-Time Environment Setup

Run these commands **once** on your Mac to set up the environment.

### Step 1: Start Docker Desktop

```bash
open -a Docker
docker ps
```

### Step 2: Create Minikube Cluster
```bash
# Start Minikube with 3GB memory

minikube start -p url-lookup-cluster --driver=docker --cpus=2 --memory=3072

# Set as default context
kubectl config use-context url-lookup-cluster

# Verify cluster is running
minikube status
kubectl get nodes
```

### Step 3: Create Namespaces
```bash
kubectl create namespace development
kubectl create namespace release
kubectl create namespace production

# Verify
kubectl get namespaces
```

### Step 4: Create Docker Hub Secret in Each Namespace
```bash
# Replace with your actual Docker Hub token
DOCKER_TOKEN="your-docker-hub-token"

for ns in development release production; do
  kubectl create secret docker-registry dockerhub-secret \
    --docker-server=docker.io \
    --docker-username=MY-USERNAME \
    --docker-password=$DOCKER_TOKEN \
    --namespace=$ns
done

# Verify secrets
kubectl get secrets -n development | grep dockerhub
```

### Step 5: Clone Your Repository
```bash
git clone https://github.com/MY-USERNAME/url-lookup-service.git
cd url-lookup-service
```

---

## Self-Hosted Runner Configuration

```bash
https://github.com/MY-USERNAME/url-lookup-service/settings/actions/runners/new
```

---

## CI/CD Pipeline Overview

### Pipeline Stages

| Stage | Runner | Description |
|-------|--------|-------------|
| get-version | self-hosted | Reads version from requirements.txt |
| security-scan | self-hosted | Trivy vulnerability scan |
| test | self-hosted | Runs pytest suite |
| deploy-development | self-hosted | Builds + deploys to development namespace |
| deploy-release | self-hosted | Builds + deploys to release namespace |
| deploy-production | self-hosted | Builds + deploys to production namespace |

---
### Image Tags Created

| Branch | Image Tag Format | Example |
|--------|-----------------|---------|
| development | `development_{version}_{commit}` | `my-user/url-lookup-service:development_1.0.0_abc1234` |
| release | `release_{version}_{commit}` | `my-user/url-lookup-service:release_1.0.0_abc1234` |
| main | `production_{version}_{commit}` | `my-user/url-lookup-service:production_1.0.0_abc1234` |

---

## Deployment Commands

### Check Deployment Status

```bash
# View pods
kubectl get pods -n development
kubectl get pods -n release
kubectl get pods -n production

# View services
kubectl get svc -n development

# View deployment status
kubectl rollout status deployment/url-lookup -n development
```

## Access App
```bash
# Port forward to localhost
kubectl port-forward service/url-lookup-service -n development 8080:80

### Open browser
open http://localhost:8080
```

## Test
```bash
# Health check
curl http://localhost:8080/health

# Check a URL
curl "http://localhost:8080/urlinfo/1/https://google.com"

# Add a malware URL
curl -X POST http://localhost:8080/admin/add \
  -H "Content-Type: application/json" \
  -d '{"url": "http://evil.com"}'

# List blocked URLs
curl http://localhost:8080/admin/list
```

---

## Rollback

```bash
kubectl set image deployment/url-lookup \
  url-lookup=my-username/url-lookup-service:development_0.9.0_def5678 \
  -n development

## View deployment history
kubectl rollout history deployment/url-lookup -n development

# Rollback to previous version
kubectl rollout undo deployment/url-lookup -n development

# Rollback to specific revision
kubectl rollout undo deployment/url-lookup -n development --to-revision=2

# check rollout
kubectl rollout status deployment/url-lookup -n development
```
## Stop & Delete
```bash
# Stop Minikube
minikube stop -p url-lookup-cluster

# Delete Minikube cluster
minikube delete -p url-lookup-cluster
```

## Troubleshooting

### Check if Minikube is Running
```bash
# Check Minikube status
minikube status

# Check specific profile
minikube status -p url-lookup-cluster

# List all profiles
minikube profile list
```

### Check if cluster is Created
```bash
# Get cluster info
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check cluster version
kubectl version
```

### Check if Docker inside Minikube is Running
```bash
# Switch to Minikube's Docker daemon
eval $(minikube -p url-lookup-cluster docker-env)

# Check Docker status
docker ps

# Check images inside Minikube
docker images
```

### Check Pods status
```bash
# Check pods
kubectl get pods -n development
kubectl get pods -n release
kubectl get pods -n production

# Check all pods across all namespaces
kubectl get pods -A

# Check pods with more details
kubectl get pods -n development -o wide

# Watch pods in real-time
kubectl get pods -n development -w
```

### Check Pod logs
```bash
# Check logs of a specific pod
kubectl logs my-pod -n development

# Check last 50 lines
kubectl logs my-pod -n development --tail=50

# Follow logs in real-time
kubectl logs my-pod -n development -f
```