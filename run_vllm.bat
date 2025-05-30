@echo off

REM ========================================
REM           Configuration Variables
REM ========================================
set WSL_DISTRO=Ubuntu-24.04
set MODEL_PATH=/home/kn/models/Qwen3-4B-AWQ
set MODEL_NAME=Qwen3-4B
set MAX_LEN=10240
set HOST_PORT=8000
set CONTAINER_PORT=8000
set DOCKER_IMAGE=vllm/vllm-openai:v0.9.0
set CONTAINER_NAME=vllm-server
set GPU_MEMORY_UTIL=0.9
set MAX_NUM_SEQS=256
set TOOL_PARSER=hermes
set TENSOR_PARALLEL=1
set DTYPE=auto
set TRUST_REMOTE_CODE=true
set ENABLE_AUTO_TOOL_CHOICE=true
set DISABLE_LOG_STATS=true
set DISABLE_LOG_REQUESTS=true

REM ========================================
REM           Dynamic Flag Generation
REM ========================================
REM Trust remote code flag
if /i "%TRUST_REMOTE_CODE%"=="true" (
    set TRUST_FLAG=--trust-remote-code
) else (
    set TRUST_FLAG=
)

REM Auto tool choice flag
if /i "%ENABLE_AUTO_TOOL_CHOICE%"=="true" (
    set TOOL_CHOICE_FLAG=--enable-auto-tool-choice
) else (
    set TOOL_CHOICE_FLAG=
)

REM Log stats flag
if /i "%DISABLE_LOG_STATS%"=="true" (
    set LOG_STATS_FLAG=--disable-log-stats
) else (
    set LOG_STATS_FLAG=
)

REM Log requests flag
if /i "%DISABLE_LOG_REQUESTS%"=="true" (
    set LOG_REQUESTS_FLAG=--disable-log-requests
) else (
    set LOG_REQUESTS_FLAG=
)

REM Tool parser flag
if not "%TOOL_PARSER%"=="" (
    set TOOL_PARSER_FLAG=--tool-call-parser %TOOL_PARSER%
) else (
    set TOOL_PARSER_FLAG=
)

REM Tensor parallel flag
if %TENSOR_PARALLEL% GTR 1 (
    set TENSOR_PARALLEL_FLAG=--tensor-parallel-size %TENSOR_PARALLEL%
) else (
    set TENSOR_PARALLEL_FLAG=
)

REM Data type flag
if not "%DTYPE%"=="auto" (
    set DTYPE_FLAG=--dtype %DTYPE%
) else (
    set DTYPE_FLAG=
)

echo ========================================
echo         vLLM Server Startup Script
echo ========================================
echo Configuration:
echo - WSL Distribution: %WSL_DISTRO%
echo - Model Path: %MODEL_PATH%
echo - Model Name: %MODEL_NAME%
echo - Max Length: %MAX_LEN% tokens
echo - Host Port: %HOST_PORT%
echo - Container Port: %CONTAINER_PORT%
echo - Docker Image: %DOCKER_IMAGE%
echo - Container Name: %CONTAINER_NAME%
echo - GPU Memory Util: %GPU_MEMORY_UTIL%
echo - Max Sequences: %MAX_NUM_SEQS%
echo - Tool Parser: %TOOL_PARSER%
echo - Tensor Parallel: %TENSOR_PARALLEL%
echo - DType: %DTYPE%
echo - Trust Remote Code: %TRUST_REMOTE_CODE%
echo - Enable Auto Tool Choice: %ENABLE_AUTO_TOOL_CHOICE%
echo - Disable Log Stats: %DISABLE_LOG_STATS%
echo - Disable Log Requests: %DISABLE_LOG_REQUESTS%
echo ========================================
echo.

echo [1/7] Checking Docker service...
wsl -d %WSL_DISTRO% -- bash -c "docker info >/dev/null 2>&1"
if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Docker service is not running
    echo [INFO] Please start Docker Desktop or Docker daemon
    echo.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Docker service is running
)
echo.

echo [2/7] Checking Docker image availability...
wsl -d %WSL_DISTRO% -- bash -c "docker image inspect %DOCKER_IMAGE% >/dev/null 2>&1"
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Docker image %DOCKER_IMAGE% not found locally
    echo [INFO] Will download image on first run (this may take several minutes)
) else (
    echo [SUCCESS] Docker image %DOCKER_IMAGE% found
)
echo.

echo [3/7] Stopping and removing existing containers...
wsl -d %WSL_DISTRO% -- bash -c "docker stop %CONTAINER_NAME% 2>/dev/null || true; docker rm %CONTAINER_NAME% 2>/dev/null || true"
echo [SUCCESS] Container %CONTAINER_NAME% cleaned up
echo.

echo [4/7] Checking if port %HOST_PORT% is available...
wsl -d %WSL_DISTRO% -- bash -c "ss -tuln | grep ':%HOST_PORT% '"
if %ERRORLEVEL% EQU 0 (
    echo [FAILED] Port %HOST_PORT% is still in use
    echo [INFO] Please wait a moment for port to be released or change HOST_PORT variable
    echo.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Port %HOST_PORT% is available
)
echo.

echo [5/7] Checking if model directory exists...
wsl -d %WSL_DISTRO% -- bash -c "if [ ! -d '%MODEL_PATH%' ]; then exit 1; fi"
if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Model directory not found: %MODEL_PATH%
    echo [INFO] Please ensure the model is downloaded to the correct path
    echo.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Model directory found: %MODEL_PATH%
)
echo.

echo [6/7] Checking GPU availability and memory...
wsl -d %WSL_DISTRO% -- bash -c "nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits 2>/dev/null"
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] NVIDIA GPU not detected - using CPU mode
) else (
    echo [SUCCESS] NVIDIA GPU detected with above specifications
)
echo.

echo [7/7] Starting vLLM server...
echo - Image: %DOCKER_IMAGE%
echo - Container: %CONTAINER_NAME%
echo - Port Mapping: %HOST_PORT%:%CONTAINER_PORT%
echo - GPU Memory: %GPU_MEMORY_UTIL%
echo - Max Sequences: %MAX_NUM_SEQS%
echo - Tensor Parallel: %TENSOR_PARALLEL%
echo.
echo ========================================
echo           Server Information
echo ========================================
echo Server URL:  http://localhost:%HOST_PORT%
echo API Docs:    http://localhost:%HOST_PORT%/docs
echo Health:      http://localhost:%HOST_PORT%/health
echo Models:      http://localhost:%HOST_PORT%/v1/models
echo ========================================
echo.
echo [INFO] Server will start now and run in foreground
echo [INFO] To stop the server: Press Ctrl+C
echo [INFO] To run in background: Add -d flag to docker run command
echo.

REM ========================================
REM           Docker Container Execution
REM ========================================
wsl -d %WSL_DISTRO% -- bash -c ^
"docker run ^
--name %CONTAINER_NAME% ^
--gpus all ^
--ipc=host ^
-p %HOST_PORT%:%CONTAINER_PORT% ^
-e HF_HUB_DISABLE_TELEMETRY=1 ^
-e TOKENIZERS_PARALLELISM=false ^
-v %MODEL_PATH%:/model ^
%DOCKER_IMAGE% ^
--model /model ^
--served-model-name %MODEL_NAME% ^
--max-model-len %MAX_LEN% ^
--gpu-memory-utilization %GPU_MEMORY_UTIL% ^
--max-num-seqs %MAX_NUM_SEQS% ^
%TENSOR_PARALLEL_FLAG% ^
%DTYPE_FLAG% ^
%TRUST_FLAG% ^
%TOOL_CHOICE_FLAG% ^
%TOOL_PARSER_FLAG% ^
%LOG_STATS_FLAG% ^
%LOG_REQUESTS_FLAG%"

cmd /k