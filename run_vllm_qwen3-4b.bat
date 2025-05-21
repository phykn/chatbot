@echo off

wsl -d Ubuntu-24.04 -- bash -c ^
"docker run --gpus all --ipc=host -p 8000:8000 ^
-v /home/kn/models/Qwen3-4B-AWQ:/model ^
vllm/vllm-openai:latest ^
--model /model ^
--served-model-name Qwen3-4B-AWQ ^
--max-model-len 8192 ^
--enable-auto-tool-choice ^
--tool-call-parser=hermes"

cmd /k
