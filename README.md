# IoT Project Demo

Sample demo app

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: Next.js with React and Tailwind CSS
- **Database**: PostgreSQL
- **Orchestration**: Kubernetes with Kind
- **Ingress**: Traefik with TLS termination
- **Domain**: myiot.local (with SSL certificates)

## Prerequisites

### WSL2 Setup

1. **Enable WSL2** (if not already enabled):
   ```powershell
   # Run in PowerShell as Administrator
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

2. **Install Ubuntu 22.04 LTS** from Microsoft Store

3. **Set WSL2 as default**:
   ```powershell
   wsl --set-default-version 2
   ```

4. **Update WSL2**:
   ```powershell
   wsl --update
   ```

### Required Software in WSL2

# Install the following packages in your WSL2 Ubuntu environment:

```
# Update package list
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git vim

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Install mkcert for SSL certificates
sudo apt install mkcert
```

## SSL Certificate Setup

1. **Install mkcert CA**:
   ```bash
   mkcert -install
   ```

2. **Generate certificates for myiot.local**:
   ```bash
   # Create certificates directory
   mkdir -p certs
   
   # Generate certificates
   mkcert -key-file certs/myiot.local-key.pem -cert-file certs/myiot.local.pem myiot.local localhost 127.0.0.1
   ```

3. **Add myiot.local to hosts file**:
   ```bash
   echo "127.0.0.1 myiot.local" | sudo tee -a /etc/hosts
   ```

## Project Setup

1. **Clone and navigate to project**:
   ```bash
   git clone https://github.com/RamyaVini/IOT-project-demo.git
   cd IOT-project-demo
   ```

2. **Build Docker images**:
   ```bash
   # Build backend image
   docker build -t backend-iot:latest ./backend/
   
   # Build frontend image
   docker build -t frontend-iot:latest ./frontend/
   ```

3. **Load images into Kind**:
   ```bash
   # Create Kind cluster
   kind create cluster --config=manifests/kind-config.yaml
   
   # Load images into Kind
   kind load docker-image backend-iot:latest
   kind load docker-image frontend-iot:latest
   ```

## Kubernetes Deployment

### 1. Install Traefik Ingress Controller

```bash
# Install Helm and Traefik
# For installing HELM refer link https://helm.sh/docs/intro/install/#from-script 

helm repo add traefik https://helm.traefik.io/traefik
helm repo update
kubectl create namespace traefik

helm install traefik traefik/traefik \
  --namespace traefik \
  --set service.type=NodePort \
  --set ports.web.nodePort=30080 \
  --set ports.websecure.nodePort=30443 \
  --set ingressClass.isDefaultClass=true


### 2. Create TLS Secret

```bash
# Create TLS secret from certificates
kubectl create secret tls iot-tls --cert=certs/myiot.local.pem --key=certs/myiot.local-key.pem
```

### 3. Deploy Applications (in sequence)

**Step 1: Deploy Database**
```bash
kubectl apply -f manifests/postgres.yaml
```

Wait for PostgreSQL to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
```

**Step 2: Deploy Backend**
```bash
kubectl apply -f manifests/backend.yaml
```

Wait for backend to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=backend-iot --timeout=300s
```

**Step 3: Deploy Frontend**
```bash
kubectl apply -f manifests/frontend.yaml
```

Wait for frontend to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=frontend-iot --timeout=300s
```

**Step 4: Deploy Ingress**
```bash
kubectl apply -f manifests/ingress.yaml
```

## Verification and Testing

### 1. Check Pod Status

```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

### 2. Test Backend API

```bash
# Check event endpoint
curl -k https://myiot.local/api/events

# Test API documentation
curl -k https://myiot.local/docs

# Submit test data
curl -k -X POST "https://myiot.local/api/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "PV001",
    "timestamp": "2024-01-15T10:30:00Z",
    "location": {
      "site": "Solar Farm Alpha",
      "coordinates": {
        "lat": 37.7749,
        "lon": -122.4194
      }
    },
    "measurements": {
      "ac_power": 1500.5,
      "dc_voltage": 48.2,
      "dc_current": 31.1,
      "temperature_module": 45.3,
      "temperature_ambient": 28.7
    },
    "status": {
      "operational": true,
      "fault_code": null
    },
    "meta_info": {
      "firmware_version": "v2.1.3",
      "connection_type": "4G"
    }
  }'
```

### 3. Test Frontend UI

1. **Open browser** and navigate to: `https://myiot.local/ui`
2. **Accept SSL certificate** (self-signed)
3. **Verify UI loads** with the PV Device Events table
4. **Test functionality**:
   - Search by device ID
   - Filter by date
   - Navigate pagination
   - View submitted data

### 4. Test API Endpoints

```bash
# Get all events
curl -k https://myiot.local/api/events

# Get OpenAPI spec
curl -k https://myiot.local/openapi.json

# Access API documentation
# Open: https://myiot.local/docs
```

### Cleanup

```bash
# Delete all resources
kubectl delete -f manifests/

# Delete Kind cluster
kind delete cluster

# Remove certificates
rm -rf certs/
```
