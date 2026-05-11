# URL Lookup Service

A lightweight URL safety checker with Redis Pub/Sub for real-time updates across multiple instances. Built with Flask, Redis, and Kubernetes.

## Features

- Check if a URL is safe or malicious
- Redis Pub/Sub for real-time updates across all instances
- Docker and Docker Compose for local development
- Kubernetes deployment with HPA auto-scaling
- Simple web interface
- Admin API for managing blocked URLs

## Quick Start

### Prerequisites

- Docker Desktop (for Docker Compose) - available for Windows, macOS, and Linux
- Minikube (optional, for Kubernetes)

## Running with Docker Compose

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/url-lookup-service.git
cd url-lookup-service
```

### Step 2: Start the services

```bash
docker compose up --build
```

This starts:
- Redis on port `6379`
- 2 instances of the URL lookup service on ports `8080` and `8081`

### Step 3: Test the service

```bash
# Health check
curl http://localhost:8080/health

# Check a URL
curl "http://localhost:8080/urlinfo/1/https://google.com"

# Add a malware URL
curl -X POST http://localhost:8080/admin/add \
  -H "Content-Type: application/json" \
  -d '{"url": "http://evil.com"}'

# Check again = now blocked 
curl "http://localhost:8080/urlinfo/1/http://evil.com"

# List all blocked URLs
curl http://localhost:8080/admin/list
```

### Step 4: Open the web interface

```bash
# Windows
start http://localhost:8080

# macOS
open http://localhost:8080

# Linux
xdg-open http://localhost:8080
```

### Step 5: Scale to more instances

```bash
# Scale to 5 instances
docker compose up -d --scale url-lookup=5

# Check running instances
docker compose ps
```

### Step 6: Stop everything

```bash
docker compose down
```

## Running with Minikube (Kubernetes)

### Prerequisites

Install Minikube:
```bash
# Windows (using Chocolatey)
choco install minikube

# Windows (using winget)
winget install minikube

# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Step 1: Start Minikube

```bash
minikube start --driver=docker --cpus=2 --memory=4096
```

### Step 2: Build the Docker image inside Minikube

```bash
# Switch to Minikube's Docker daemon
eval $(minikube docker-env)

# Build the image
docker build -t url-lookup:latest .
```

### Step 3: Deploy to Kubernetes

```bash
# Create Redis deployment and service
kubectl apply -f k8s/redis-deployment.yaml

# Create URL lookup deployment and service
kubectl apply -f k8s/url-lookup-deployment.yaml

# Create Horizontal Pod Autoscaler (HPA)
kubectl apply -f k8s/hpa.yaml

# Check pods
kubectl get pods -l app=url-lookup
```

### Step 4: Access the service

```bash
minikube service url-lookup-service
```

### Step 8: Clean up

```bash
kubectl delete -f k8s/
minikube stop
```

## Pub/Sub in Action

The service uses Redis Pub/Sub to propagate URL updates across ALL instances in real-time:

```bash
# Start multiple instances (Docker Compose)
docker compose up --scale url-lookup=3

# Add a URL through instance 1 (port 8080)
curl -X POST http://localhost:8080/admin/add \
  -H "Content-Type: application/json" \
  -d '{"url": "http://evil.com"}'

# Instance 2 (port 8081) already knows
curl http://localhost:8081/urlinfo/1/http://evil.com
```

## Admin API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/urlinfo/1/{url}` | Check if URL is safe |
| POST | `/admin/add` | Add URL to block list |
| POST | `/admin/remove` | Remove URL from block list |
| GET | `/admin/list` | List all blocked URLs |

### Example API usage:

```bash
# Add a URL
curl -X POST http://localhost:8080/admin/add \
  -H "Content-Type: application/json" \
  -d '{"url": "http://phishing.com"}'

# Check if blocked
curl "http://localhost:8080/urlinfo/1/http://phishing.com"

# List all blocked URLs
curl http://localhost:8080/admin/list

# Remove a URL
curl -X POST http://localhost:8080/admin/remove \
  -H "Content-Type: application/json" \
  -d '{"url": "http://phishing.com"}'
```

## Project Structure

```
url-lookup-service/
├── url-lookup-service.py   # Main Flask application
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container build file
├── docker-compose.yml      # Local orchestration
├── static/
│   └── index.html          # Web interface
└── k8s/
    ├── redis-deployment.yaml      # Redis for K8s
    ├── url-lookup-deployment.yaml  # App for K8s
    └── hpa.yaml                    # Auto-scaling rules
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `PORT` | `8080` | Application port |

## Auto-scaling (Kubernetes)

The HPA is configured to scale based on:

- **CPU**: Scale when average CPU > 50%
- **Memory**: Scale when average memory > 70%

```yaml
minReplicas: 2
maxReplicas: 5
```

## Troubleshooting

### Port already in use

```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# macOS / Linux
lsof -i :8080
kill -9 <PID>
```

### Redis connection refused

```bash
# Check if Redis is running
docker compose ps redis

# Restart Redis
docker compose restart redis
```

### Minikube metrics not showing

```bash
# Enable metrics-server
minikube addons enable metrics-server
```

## Load Balancer external IP shows pending

```bash
# Start Minikube tunnel in a separate terminal
minikube tunnel


# Wait a few seconds, then check again
kubectl get svc url-lookup-service

# macOS
open http://EXTERNAL-IP
```

## License

MIT

## Contributing

1. Create a feature branch from `development`
2. Make your changes
3. Push to your branch
4. Open a Pull Request to `development`