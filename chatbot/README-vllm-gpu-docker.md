# vLLM LLM Server Setup Guide (with NVIDIA GPU & Docker)

This guide describes how to set up a Large Language Model (LLM) server using [vLLM](https://github.com/vllm-project/vllm) with NVIDIA GPU support via Docker.  
It covers all steps, including NVIDIA driver installation, Docker/NVIDIA integration, and model serving.

## 1. Environment Preparation
- **OS:** Ubuntu 24.04 (or WSL2)
- **NVIDIA GPU Driver:**  
  Ensure the official NVIDIA driver is installed and working: `nvidia-smi`

This should display your GPU information.

## 2. Docker & NVIDIA Container Toolkit Setup

### 2.1 Install Docker  
Refer to the [official Docker documentation](https://docs.docker.com/engine/install/) if not already installed.

### 2.2 Install NVIDIA Container Toolkit (Official Method)

```
# 1. Add NVIDIA GPG key

sudo wget -qO /etc/apt/keyrings/nvidia-container-toolkit.asc https://nvidia.github.io/libnvidia-container/gpgkey

# 2. Register NVIDIA apt repository (using echo)

echo "deb [signed-by=/etc/apt/keyrings/nvidia-container-toolkit.asc] https://nvidia.github.io/libnvidia-container/stable/deb/amd64 /" | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 3. Update package list

sudo apt-get update

# 4. Install nvidia-container-toolkit

sudo apt-get install -y nvidia-container-toolkit

# 5. Restart Docker

sudo systemctl restart docker
```

## 3. Verify GPU Integration

- **On the host:**
```
nvidia-smi
```

- **Inside Docker:**
```
docker run --gpus all nvidia/cuda:12.9.0-devel-ubuntu24.04 nvidia-smi
```
Both commands should display your GPU info. If not, check your driver/toolkit installation.

## 4. Pull the Official vLLM Docker Image

```
docker pull vllm/vllm-openai:latest
```

## 5. Run the LLM Server

### 5.1 Serve a Hugging Face Model Directly
```
docker run --gpus all --ipc=host -p 8000:8000 vllm/vllm-openai:latest \
  --model <huggingface_model_path>
```

### 5.2 Serve a Local Model
```
docker run --gpus all --ipc=host -p 8000:8000 \
  -v /path/to/your/local/models:/models \
  vllm/vllm-openai:latest \
  --model /models/<your_model_directory_or_file>
```
Replace /path/to/your/local/models with the actual directory on your computer where your model files are stored.
Then, replace <your_model_directory_or_file> with the specific folder or file name of the model you want to serve.

## 6. Confirm the Server is Running
Check with:
```
curl http://localhost:8000/v1/models
```
You should see a list of available models.

## 7. Troubleshooting
- **Docker cannot access GPU:**  
  Double-check NVIDIA driver, nvidia-container-toolkit installation, Docker restart, and repository registration (using echo).
- **pip/torch/vllm build issues:**  
  Always use the official image `vllm/vllm-openai:latest` to avoid manual build problems.

## 8. Key Commands Summary
```
# Register NVIDIA repository (with echo)

sudo wget -qO /etc/apt/keyrings/nvidia-container-toolkit.asc https://nvidia.github.io/libnvidia-container/gpgkey

echo "deb [signed-by=/etc/apt/keyrings/nvidia-container-toolkit.asc] https://nvidia.github.io/libnvidia-container/stable/deb/amd64 /" | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update

sudo apt-get install -y nvidia-container-toolkit

sudo systemctl restart docker


# Verify GPU

nvidia-smi

docker run --gpus all nvidia/cuda:12.9.0-devel-ubuntu24.04 nvidia-smi


# Run vLLM LLM server

docker pull vllm/vllm-openai:latest

docker run --gpus all --ipc=host -p 8000:8000 vllm/vllm-openai:latest --model Qwen/Qwen3-4B
```