# MLOps PyTorch Pipeline
A production-style ML pipeline for PyTorch training and serving using Docker and Kubernetes.

Run the following script in your macOS Terminal from inside your mlops-pytorch-pipeline folder. It will generate a clean, comprehensive README.md with an ASCII architecture diagram, clear setup instructions, and push it directly to GitHub:

cat << 'EOF' > README.md
# MLOps PyTorch Pipeline

An end-to-end Machine Learning Operations (MLOps) pipeline demonstrating containerized PyTorch model training and resilient Kubernetes serving with autoscaling on CIFAR-10.

---

## 🏗 System Architecture

```text
                               +----------------------------------+
                               |     Git Workflow (PR & CI)       |
                               +-----------------+----------------+
                                                 |
                                                 v
                               +----------------------------------+
                               |    Docker Multi-Stage Builds     |
                               +--------+----------------+--------+
                                        |                |
                       +----------------+                +---------------+
                       | mlops-train:v1                                  | mlops-serve:v1
                       v                                                 v
  +-------------------------------------------+    +-------------------------------------------+
  |        Kubernetes Training Job            |    |       Kubernetes Serving Deployment       |
  |                                           |    |                                           |
  |  +----------------+   +----------------+  |    |  +----------------+   +----------------+  |
  |  |   ConfigMap    |   | Training Job   |  |    |  |  Replica 1     |   |  Replica 2     |  |
  |  | (config.yaml)  |-->|  (train.py)    |  |    |  | (FastAPI App)  |   | (FastAPI App)  |  |
  |  +----------------+   +--------+-------+  |    |  +--------+-------+   +--------+-------+  |
  +--------------------------------|----------+    +-----------|--------------------|----------+
                                   |                           |                    |
                                   v                           +----------+---------+
                        +----------------------+                          |
                        |   Storage (PVC)      |<-------------------------+ (Read-Only)
                        |  /app/data           |
                        |  /app/checkpoints    |
                        +----------------------+
                                                                          ^
                                                                          |
                                                      +-------------------+-------------------+
                                                      |   Kubernetes Service (ClusterIP: 80)  |
                                                      +-------------------+-------------------+
                                                                          ^
                                                                          |
                                                      +-------------------+-------------------+
                                                      |     HPA (Auto-scale 2-5 pods)         |
                                                      +-------------------+-------------------+
                                                                          ^
                                                                          |
                                                      +-------------------+-------------------+
                                                      | Client (curl POST /predict)           |
                                                      +---------------------------------------+

**📁 Repository Structure**

mlops-pytorch-pipeline/
├── .github/workflows/ci.yml       # GitHub Actions CI syntax pipeline
├── configs/
│   └── training_config.yaml       # Hyperparameters & dataset configuration
├── docker/
│   ├── Dockerfile.train           # Multi-stage build for training runtime
│   └── Dockerfile.serve           # Slim, non-root runtime for model inference
├── k8s/
│   ├── namespace.yaml             # Dedicated namespace (ml-training)
│   ├── configmap.yaml             # ConfigMap mounting training hyperparameters
│   ├── pvc.yaml                   # Persistent Volume Claim for data & checkpoints
│   ├── training-job.yaml          # Batch Job for PyTorch model training
│   ├── serving-deployment.yaml    # 2-replica Deployment with liveness/readiness probes
│   ├── serving-service.yaml       # ClusterIP Service routing to port 8080
│   └── hpa.yaml                   # Horizontal Pod Autoscaler based on CPU usage
├── requirements/
│   ├── train.txt                  # Pinned training dependencies
│   └── serve.txt                  # Pinned inference dependencies
├── src/
│   ├── dataset.py                 # CIFAR-10 data loaders & augmentations
│   ├── model.py                   # ResNet-18 model architecture adaptation
│   ├── serve.py                   # FastAPI prediction service (/health, /predict)
│   └── train.py                   # Training loop with structured JSON logging
├── .gitignore
└── README.md

**🚀 Setup and Execution Instructions**
**Prerequisites**
macOS / Linux environment

Docker Desktop installed and running

minikube and kubectl installed

**1. Local Container Build & Verification**

# Build training container
docker build -f docker/Dockerfile.train -t mlops-train:v1 .

# Run training locally with mounted volumes
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/checkpoints:/app/checkpoints \
  mlops-train:v1

# Build serving container
docker build -f docker/Dockerfile.serve -t mlops-serve:v1 .

# Run serving locally
docker run --rm -p 8080:8080 \
  -v $(pwd)/checkpoints:/app/checkpoints \
  mlops-serve:v1

**2. Kubernetes Cluster Deployment (Minikube)**

# 1. Point local terminal to Minikube Docker Daemon
eval $(minikube docker-env)

# 2. Build images inside Minikube environment
docker build -f docker/Dockerfile.train -t mlops-train:v1 .
docker build -f docker/Dockerfile.serve -t mlops-serve:v1 .

# 3. Create Namespace, ConfigMap, and Storage PVC
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml

# 4. Trigger the PyTorch Training Job
kubectl apply -f k8s/training-job.yaml

# Monitor Training Job execution
kubectl get jobs -n ml-training
kubectl logs -f job/pytorch-training-job -n ml-training

# 5. Deploy Serving Layer, Service, and HPA
kubectl apply -f k8s/serving-deployment.yaml
kubectl apply -f k8s/serving-service.yaml
kubectl apply -f k8s/hpa.yaml

# Verify healthy pods and deployment status
kubectl get pods -n ml-training
kubectl describe deployment model-serving -n ml-training

**3. Testing Inference Endpoints**

# Forward port 8080 from ClusterIP Service
kubectl port-forward svc/model-serving 8080:80 -n ml-training

# Health Check
curl http://localhost:8080/health

# Send Prediction Request
curl -X POST http://localhost:8080/predict -F "image=@test_image.png"


Stage, commit, and push the README to GitHub
git add README.md
git commit -m "docs: add comprehensive README with architecture diagram and setup steps"
git push origin main

Sync develop branch
git checkout develop
git merge main
git push origin develop
git checkout main

After running this script, refresh your GitHub repository page in the browser to view the formatted `README.md` with the architecture diagram and documentation
